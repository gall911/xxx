# world/systems/zone_manager.py
"""
区域管理器 - 智能同步版
支持: 增量更新、版本控制、数据保护
"""

import os
import yaml
from pathlib import Path
from evennia import create_object, search_object, search_tag
from evennia.utils import logger
from django.conf import settings


class ZoneManager:
    """区域管理器"""
    
    ZONES_DIR = Path(settings.GAME_DIR) / "data" / "zones"
    
    # ========== 区域加载 ==========
    
    @staticmethod
    def load_zone_config(zone_key):
        """加载区域配置"""
        zone_path = ZoneManager.ZONES_DIR / zone_key
        
        if not zone_path.exists():
            logger.log_err(f"[Zone] 区域不存在: {zone_key}")
            return None
        
        # 加载所有 YAML 文件
        config = {}
        
        for yaml_file in zone_path.glob("*.yaml"):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    config[yaml_file.stem] = data
            except Exception as e:
                logger.log_err(f"[Zone] 加载失败 {yaml_file}: {e}")
        
        return config
    
    @staticmethod
    def list_all_zones():
        """列出所有区域"""
        zones = {}
        
        if not ZoneManager.ZONES_DIR.exists():
            return zones
        
        for zone_dir in ZoneManager.ZONES_DIR.iterdir():
            if zone_dir.is_dir() and not zone_dir.name.startswith('_'):
                zone_key = zone_dir.name
                
                # 检查是否已建造
                existing = search_tag(f'zone:{zone_key}')
                
                # 检查是否激活
                active_objects = [obj for obj in existing if obj.db.zone_active != False]
                
                zones[zone_key] = {
                    'built': len(existing) > 0,
                    'active': len(active_objects) > 0,
                    'object_count': len(existing)
                }
        
        return zones
    
    # ========== 区域建造 ==========
    
    @staticmethod
    def build_zone(zone_key):
        """
        建造区域 (首次创建)
        
        Args:
            zone_key: 区域标识
        
        Returns:
            bool: 是否成功
        """
        config = ZoneManager.load_zone_config(zone_key)
        if not config:
            return False
        
        logger.log_info(f"[Zone] 开始建造区域: {zone_key}")
        
        # 1. 建造房间
        rooms = config.get('rooms', {}).get('rooms', {})
        room_objects = {}
        
        for room_key, room_data in rooms.items():
            room_obj = ZoneManager._build_room(room_key, room_data, zone_key)
            if room_obj:
                room_objects[room_key] = room_obj
        
        # 2. 连接出口
        for room_key, room_data in rooms.items():
            exits = room_data.get('exits', {})
            if exits and room_key in room_objects:
                ZoneManager._build_exits(room_objects[room_key], exits, room_objects)
        
        # 3. 生成NPC
        npcs = config.get('npcs', {}).get('npcs', {})
        for npc_key, npc_data in npcs.items():
            spawn_room_key = npc_data.get('spawn_room')
            if spawn_room_key and spawn_room_key in room_objects:
                ZoneManager._build_npc(npc_key, npc_data, room_objects[spawn_room_key], zone_key)
        
        # 4. 记录版本
        ZoneManager._save_zone_version(zone_key, config.get('version', {}))
        
        logger.log_info(f"[Zone] 区域建造完成: {zone_key}")
        return True
    
    @staticmethod
    def _build_room(room_key, room_data, zone_key):
        """建造单个房间"""
        # 检查是否已存在
        existing = search_object(room_key, typeclass='typeclasses.rooms.Room')
        if existing:
            logger.log_warn(f"[Zone] 房间已存在,跳过: {room_key}")
            return existing[0]
        
        # 创建房间
        room = create_object(
            'typeclasses.rooms.Room',
            key=room_key,
            location=None
        )
        
        # 设置属性
        room.db.desc = room_data.get('desc', '')
        room.name = room_data.get('name', room_key)
        room.db.zone_key = zone_key
        room.db.zone_active = True
        
        # 打标签
        room.tags.add(f'zone:{zone_key}')
        room.tags.add('zone_managed')
        
        # 保存配置哈希 (用于检测变化)
        room.db.config_hash = ZoneManager._hash_config(room_data)
        
        logger.log_info(f"[Zone] 创建房间: {room_key}")
        return room
    
    @staticmethod
    def _build_exits(room, exits_data, room_objects):
        """建造出口"""
        for direction, target_key in exits_data.items():
            if target_key not in room_objects:
                continue
            
            target_room = room_objects[target_key]
            
            # 创建出口
            create_object(
                'typeclasses.exits.Exit',
                key=direction,
                location=room,
                destination=target_room
            )
    
    @staticmethod
    def _build_npc(npc_key, npc_data, spawn_room, zone_key):
        """生成NPC"""
        # 检查是否已存在
        existing = search_object(npc_key, typeclass='typeclasses.npcs.NPC')
        if existing:
            logger.log_warn(f"[Zone] NPC已存在,跳过: {npc_key}")
            return existing[0]
        
        # 创建NPC
        npc = create_object(
            'typeclasses.npcs.NPC',
            key=npc_key,
            location=spawn_room
        )
        
        # 设置属性
        npc.db.desc = npc_data.get('desc', '')
        npc.name = npc_data.get('name', npc_key)
        npc.db.zone_key = zone_key
        npc.db.zone_active = True
        npc.db.original_location = spawn_room
        npc.db.respawn_time = npc_data.get('respawn_time', 300)
        npc.db.is_alive = True
        
        # 打标签
        npc.tags.add(f'zone:{zone_key}')
        npc.tags.add('zone_managed')
        
        # 保存配置哈希
        npc.db.config_hash = ZoneManager._hash_config(npc_data)
        
        logger.log_info(f"[Zone] 创建NPC: {npc_key}")
        return npc
    
    # ========== 🔥 智能同步 ==========
    
    @staticmethod
    def sync_zone(zone_key, force_update=False):
        """
        智能同步区域 (增量更新)
        
        对比 YAML 和 DB,只更新变化的部分
        
        Args:
            zone_key: 区域标识
            force_update: 是否强制更新所有对象
        
        Returns:
            dict: 同步结果统计
        """
        config = ZoneManager.load_zone_config(zone_key)
        if not config:
            return {'error': '配置加载失败'}
        
        logger.log_info(f"[Zone] 开始同步区域: {zone_key}")
        
        stats = {
            'created': 0,
            'updated': 0,
            'deleted': 0,
            'unchanged': 0
        }
        
        # 1. 🔥 同步房间
        yaml_rooms = config.get('rooms', {}).get('rooms', {})
        db_rooms = {obj.key: obj for obj in search_tag(f'zone:{zone_key}') if obj.typename == 'Room'}
        
        # 新增的房间
        for room_key, room_data in yaml_rooms.items():
            if room_key not in db_rooms:
                ZoneManager._build_room(room_key, room_data, zone_key)
                stats['created'] += 1
            else:
                # 检查是否需要更新
                room_obj = db_rooms[room_key]
                new_hash = ZoneManager._hash_config(room_data)
                
                if force_update or room_obj.db.config_hash != new_hash:
                    # 🔥 只更新可更新的属性
                    ZoneManager._update_room(room_obj, room_data)
                    room_obj.db.config_hash = new_hash
                    stats['updated'] += 1
                else:
                    stats['unchanged'] += 1
        
        # 删除的房间 (YAML里没有但DB里有)
        for room_key, room_obj in db_rooms.items():
            if room_key not in yaml_rooms:
                logger.log_warn(f"[Zone] 删除多余房间: {room_key}")
                room_obj.delete()
                stats['deleted'] += 1
        
        # 2. 🔥 同步NPC (同理)
        yaml_npcs = config.get('npcs', {}).get('npcs', {})
        db_npcs = {obj.key: obj for obj in search_tag(f'zone:{zone_key}') if obj.typename == 'NPC'}
        
        for npc_key, npc_data in yaml_npcs.items():
            spawn_room_key = npc_data.get('spawn_room')
            spawn_room = search_object(spawn_room_key, typeclass='typeclasses.rooms.Room')
            
            if not spawn_room:
                continue
            
            if npc_key not in db_npcs:
                ZoneManager._build_npc(npc_key, npc_data, spawn_room[0], zone_key)
                stats['created'] += 1
            else:
                npc_obj = db_npcs[npc_key]
                new_hash = ZoneManager._hash_config(npc_data)
                
                if force_update or npc_obj.db.config_hash != new_hash:
                    ZoneManager._update_npc(npc_obj, npc_data, spawn_room[0])
                    npc_obj.db.config_hash = new_hash
                    stats['updated'] += 1
                else:
                    stats['unchanged'] += 1
        
        # 删除多余NPC
        for npc_key, npc_obj in db_npcs.items():
            if npc_key not in yaml_npcs:
                logger.log_warn(f"[Zone] 删除多余NPC: {npc_key}")
                npc_obj.delete()
                stats['deleted'] += 1
        
        # 3. 更新版本记录
        ZoneManager._save_zone_version(zone_key, config.get('version', {}))
        
        logger.log_info(f"[Zone] 同步完成: {stats}")
        return stats
    
    @staticmethod
    def _update_room(room_obj, room_data):
        """更新房间属性 (只更新安全的属性)"""
        # 🔥 可更新: 描述、名称
        room_obj.db.desc = room_data.get('desc', room_obj.db.desc)
        room_obj.name = room_data.get('name', room_obj.name)
        
        # 🔥 不更新: 位置、玩家添加的装饰等
        logger.log_info(f"[Zone] 更新房间: {room_obj.key}")
    
    @staticmethod
    def _update_npc(npc_obj, npc_data, spawn_room):
        """更新NPC属性"""
        npc_obj.db.desc = npc_data.get('desc', npc_obj.db.desc)
        npc_obj.name = npc_data.get('name', npc_obj.name)
        npc_obj.db.respawn_time = npc_data.get('respawn_time', npc_obj.db.respawn_time)
        
        # 🔥 只在NPC不在战斗时更新位置
        if not getattr(npc_obj.ndb, 'in_combat', False):
            npc_obj.db.original_location = spawn_room
        
        logger.log_info(f"[Zone] 更新NPC: {npc_obj.key}")
    
    # ========== 激活/休眠 ==========
    
    @staticmethod
    def activate_zone(zone_key):
        """激活区域"""
        objects = search_tag(f'zone:{zone_key}')
        
        for obj in objects:
            obj.db.zone_active = True
            
            # NPC回到出生点
            if hasattr(obj, 'db') and obj.db.original_location:
                if not getattr(obj.ndb, 'in_combat', False):
                    obj.location = obj.db.original_location
        
        logger.log_info(f"[Zone] 激活区域: {zone_key}, {len(objects)} 个对象")
    
    @staticmethod
    def deactivate_zone(zone_key):
        """休眠区域"""
        objects = search_tag(f'zone:{zone_key}')
        limbo = search_object("#2")[0]
        
        for obj in objects:
            obj.db.zone_active = False
            
            # NPC移到Limbo
            if hasattr(obj, 'location'):
                obj.location = limbo
        
        logger.log_info(f"[Zone] 休眠区域: {zone_key}, {len(objects)} 个对象")
    
    @staticmethod
    def destroy_zone(zone_key):
        """彻底删除区域 (谨慎使用)"""
        objects = search_tag(f'zone:{zone_key}')
        
        for obj in objects:
            obj.delete()
        
        logger.log_warn(f"[Zone] 删除区域: {zone_key}, {len(objects)} 个对象")
    
    # ========== 工具方法 ==========
    
    @staticmethod
    def _hash_config(config_data):
        """计算配置哈希 (用于检测变化)"""
        import hashlib
        import json
        
        config_str = json.dumps(config_data, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()
    
    @staticmethod
    def _save_zone_version(zone_key, version_data):
        """保存区域版本信息"""
        objects = search_tag(f'zone:{zone_key}')
        
        if objects:
            # 存储在第一个对象上 (通常是入口房间)
            objects[0].db.zone_version = version_data.get('version', {}).get('current', '1.0.0')
            objects[0].db.zone_last_sync = version_data.get('version', {}).get('last_sync', '')
    
    @staticmethod
    def is_zone_built(zone_key):
        """检查区域是否已建造"""
        objects = search_tag(f'zone:{zone_key}')
        return len(objects) > 0