"""
NPC管理命令 - 终极修复版 (防心累专用)
自动兼容 列表/字典/空文件/嵌套结构，怎么写都不报错
"""
import os
import yaml
from evennia import Command, create_object, search_tag
from evennia.utils.evtable import EvTable
from world.loaders.game_data import GAME_DATA
from typeclasses.npcs import NPC  # 确保你的路径是对的

# ====================================================
# 1. 原版命令 (保留不动)
# ====================================================

class CmdNPCList(Command):
    """列出所有NPC"""
    key = "xx list npc"
    aliases = ["xxln"]
    locks = "cmd:all()"
    help_category = "开发"
    
    def func(self):
        npcs = NPC.objects.all()
        if not npcs:
            self.caller.msg("没有找到任何NPC。")
            return
        
        table = EvTable("|wID|n", "|w名称|n", "|w位置|n", "|w等级|n", "|wHP|n", border="cells")
        for npc in npcs:
            hp = getattr(npc.ndb, 'hp', 0)
            max_hp = getattr(npc.ndb, 'max_hp', 0)
            loc_name = npc.location.key[:10] if npc.location else "无"
            table.add_row(
                f"#{npc.id}", 
                npc.key[:15], 
                loc_name,
                getattr(npc.ndb, 'level', 1),
                f"{hp}/{max_hp}"
            )
        self.caller.msg(table)
        self.caller.msg(f"\n总计: {len(npcs)} 个NPC")

class CmdNPCAdd(Command):
    """创建单个NPC (旧版保留)"""
    key = "xx add npc"
    aliases = ["xxan"]
    locks = "cmd:all()"
    help_category = "开发"
    
    def func(self):
        if not self.args:
            self.caller.msg("用法: xx add npc <yaml_key> [位置]")
            return
        
        args = self.args.split()
        npc_key = args[0]
        npc_data = GAME_DATA.get('npcs', {}).get(npc_key)
        if not npc_data:
            self.caller.msg(f"未在 GAME_DATA 找到: {npc_key}")
            return

        location = self.caller.location
        if len(args) > 1:
            found = self.caller.search(args[1], global_search=True)
            if found: location = found

        new_npc = create_object(NPC, key=npc_data.get('name', npc_key), location=location)
        stats = npc_data.get('stats', {})
        new_npc.ndb.hp = stats.get('max_hp', 100)
        new_npc.ndb.max_hp = stats.get('max_hp', 100)
        self.caller.msg(f"|g成功创建:|n {new_npc.key}")

class CmdNPCDelete(Command):
    """删除NPC"""
    key = "xx del npc"
    aliases = ["xxdn"]
    locks = "cmd:all()"
    help_category = "开发"
    
    def func(self):
        if not self.args:
            self.caller.msg("用法: xx del npc <目标>")
            return
        target = self.caller.search(self.args)
        if target and target.is_typeclass(NPC):
            name = target.key
            target.delete()
            self.caller.msg(f"已删除: {name}")
        else:
            self.caller.msg("找不到目标NPC。")


# ====================================================
# 2. 全自动 NPC 投放 (CmdNPCBatch - 强力兼容版)
# ====================================================

class CmdNPCBatch(Command):
    """
    全自动批量投放NPC
    
    用法: xx batch npc <yaml文件名>
    """
    
    key = "xx batch npc"
    aliases = ["xxbn"]
    locks = "cmd:all()"
    help_category = "开发"
    
    def func(self):
        if not self.args:
            self.caller.msg("用法: xx batch npc <文件名>")
            self._list_files()
            return
        
        filename = self.args.strip()
        if not filename.endswith('.yaml'): filename += ".yaml"
        file_path = os.path.join("data", "npcs", filename)
        
        if not os.path.exists(file_path):
            self.caller.msg(f"找不到文件: {file_path}")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            self.caller.msg(f"YAML解析崩溃: {e}")
            return
            
        # === 核心修复：防止 NoneType 和 List/Dict 格式混乱 ===
        if data is None:
            self.caller.msg(f"|r错误:|n 文件 {filename} 是空的！")
            return

        # 数据标准化：统一转为 [(uid, config), ...]
        processed_list = []

        # 1. 如果根节点有 'npcs' 键 (标准格式)
        if isinstance(data, dict) and 'npcs' in data:
            sub_data = data['npcs']
            if isinstance(sub_data, dict):
                for k, v in sub_data.items(): processed_list.append((k, v))
            elif isinstance(sub_data, list):
                # 这种是 {npcs: [{-id:..., ...}]}
                for item in sub_data:
                    # 尝试找唯一的ID键
                    uid = item.get('key') or item.get('id') or item.get('prototype_key')
                    if not uid: # 找不到ID就尝试用第一个key
                        keys = list(item.keys())
                        if keys: uid = keys[0]
                    processed_list.append((uid, item))

        # 2. 如果根节点本身就是列表 (List格式，你刚才报错的原因之一)
        elif isinstance(data, list):
            for item in data:
                # 兼容：列表里直接写 {-id: ...} 或 {npc_id: {...}}
                uid = item.get('key') or item.get('id') or item.get('prototype_key')
                config = item
                
                # 如果列表里是嵌套字典: - mirage_witch: {...}
                if not uid: 
                    for k, v in item.items():
                        if isinstance(v, dict):
                            uid = k
                            config = v
                            break
                
                # 还没找到uid，随便找个值做uid
                if not uid: uid = "unknown_npc"
                
                processed_list.append((uid, config))

        # 3. 如果根节点是字典，但没有 'npcs' 键 (扁平字典)
        elif isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, dict):
                    processed_list.append((k, v))
        
        if not processed_list:
            self.caller.msg("|r未发现有效的NPC数据结构。|n请检查YAML格式。")
            return

        self.caller.msg(f"|w识别到 {len(processed_list)} 个NPC配置，开始处理...|n")
        
        created_count = 0
        updated_count = 0
        
        for uid, config in processed_list:
            if not config: continue

            # 1. 寻找投放地点
            location_key = config.get('location')
            if not location_key:
                # 尝试查找 location_id (兼容 rooms.yaml 写法)
                location_key = config.get('location_id')

            location = None
            if location_key:
                # 优先 Tag (batch_room)
                found_rooms = search_tag(location_key, category="batch_room")
                if found_rooms:
                    location = found_rooms[0]
                else:
                    # 其次 名字/Key
                    found_rooms = self.caller.search(location_key, global_search=True, quiet=True)
                    if found_rooms:
                        location = found_rooms[0]
            
            if not location:
                self.caller.msg(f"|y跳过:|n NPC [{uid}] -> 未找到房间 '{location_key}'")
                continue
            
            # 2. 判断唯一性
            is_unique = config.get('unique', False)
            # 或者通过 tag 判断 (如 boss)
            if 'boss' in config.get('tags', []): is_unique = True
            
            existing_npc = None
            if is_unique:
                found_npcs = search_tag(uid, category="batch_npc")
                if found_npcs:
                    existing_npc = found_npcs[0]
                    self.caller.msg(f"更新BOSS: {uid}")
            
            # 3. 创建实体
            # 获取名字 (兼容 diverse key names)
            name_str = config.get('name', uid)
            
            if existing_npc:
                npc = existing_npc
                updated_count += 1
            else:
                npc = create_object(
                    NPC,
                    key=uid, # 内部Key使用英文ID
                    location=location,
                    tags=[(uid, "batch_npc")] if is_unique else []
                )
                created_count += 1
                if not is_unique:
                    self.caller.msg(f"投放: {name_str} -> {location.key}")

            # 4. 设置属性
            # 处理名字与显示 (Name & Aliases)
            npc.db.cname = name_str # 存带颜色的中文名，供return_appearance使用
            npc.db.color_name = name_str # 双保险
            
            # 去除颜色存为别名
            from evennia.utils.ansi import strip_ansi
            clean_name = strip_ansi(name_str)
            if clean_name != uid:
                npc.aliases.add(clean_name)

            # 描述
            if 'desc' in config:
                npc.db.desc = config['desc']
            
            # 基础数据
            stats = config.get('stats', {})
            npc.db.stats = stats
            
            # 刷新内存数据
            npc.ndb.hp = stats.get('max_hp', 100)
            npc.ndb.max_hp = stats.get('max_hp', 100)
            npc.ndb.qi = stats.get('max_qi', 100)
            npc.ndb.max_qi = stats.get('max_qi', 100)
            npc.ndb.level = stats.get('level', 1)
            
            # 技能掉落
            if 'skills' in config: npc.db.skills = config['skills']
            if 'drops' in config: npc.db.drops = config['drops']
            if 'interval' in config: npc.db.interval = config['interval']
            if 'random_dialogue' in config: npc.db.random_dialogue = config['random_dialogue']
            
            # 启动说话AI (如果刚才修改了characters.py)
            if hasattr(npc, 'start_chatter'):
                npc.start_chatter()

        self.caller.msg(f"|g完成! 新增: {created_count}, 更新: {updated_count}|n")

    def _list_files(self):
        try:
            path = os.path.join("data", "npcs")
            if not os.path.exists(path): os.makedirs(path)
            files = [f for f in os.listdir(path) if f.endswith('.yaml')]
            self.caller.msg("可用文件: " + ", ".join(files))
        except:
            pass