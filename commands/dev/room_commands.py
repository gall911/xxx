"""
房间管理命令 - 终极修复版
自动兼容 ID 连接和中文名连接，拯救心累
"""
import os
import yaml
from evennia import Command, create_object, search_tag
from evennia.utils.search import search_object
from evennia.utils.evtable import EvTable
from world.loaders.game_data import GAME_DATA
from typeclasses.rooms import Room
from typeclasses.exits import Exit

# =============================================================
# 1. 原版命令 (保留不动)
# =============================================================

class CmdRoomList(Command):
    """
    列出所有房间
    """
    key = "xx list room"
    aliases = ["xxlr"]
    locks = "cmd:all()"
    help_category = "开发"
    
    def func(self):
        rooms = Room.objects.all()
        if not rooms:
            self.caller.msg("没有找到任何房间。")
            return
        
        for room in rooms:
            desc = room.db.desc if room.db.desc else ""
            room_line = f"|[300 #{room.id}|n |115 |lc@tel #{room.id}|lt{room.key}|le|n"
            if desc:
                room_line += f" - {desc[:11]}..."
            self.caller.msg(room_line)
        self.caller.msg(f"\n总计: {len(rooms)} 个房间")

class CmdRoomAdd(Command):
    """
    旧版创建 (保留)
    """
    key = "xx add room"
    aliases = ["xxar"]
    locks = "cmd:all()"
    help_category = "开发"
    
    def func(self):
        if not self.args: return
        room_key = self.args.strip()
        room_data = GAME_DATA['rooms'].get(room_key)
        if not room_data: return
        new_room = create_object(Room, key=room_data.get('key', room_key))
        new_room.db.desc = room_data.get('desc', '未定义描述')
        self.caller.msg(f"|g成功创建:|n {new_room.key}")

class CmdRoomConnect(Command):
    """
    旧版连接 (保留)
    """
    key = "xx connect rooms"
    aliases = ["xxcr"]
    locks = "cmd:all()"
    help_category = "开发"
    def func(self): pass

# =============================================================
# 2. 全自动批量命令 (智能识别 ID 和 中文名)
# =============================================================

class CmdRoomBatch(Command):
    """
    全自动批量创建/更新房间与出口
    
    用法: xx batch room <yaml文件名>
    """
    
    key = "xx batch room"
    aliases = ["xxbr"]
    locks = "cmd:all()"
    help_category = "开发"
    
    def func(self):
        if not self.args:
            self.caller.msg("用法: xx batch room <文件名>")
            self._list_files()
            return
        
        filename = self.args.strip()
        if not filename.endswith('.yaml'): filename += ".yaml"
        file_path = os.path.join("data", "rooms", filename)
        
        if not os.path.exists(file_path):
            self.caller.msg(f"找不到文件: {file_path}")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            self.caller.msg(f"YAML错误: {e}")
            return

        rooms_data_source = data.get('rooms')
        if not rooms_data_source:
             self.caller.msg(f"错误: YAML文件中没有 'rooms:' 顶层key")
             return

        # =====================================================
        # 数据标准化：提取 (ID, 中文名Key, 配置内容)
        # =====================================================
        processed_list = []

        if isinstance(rooms_data_source, list):
            for item in rooms_data_source:
                uid = item.get('id')
                config = None
                struct_name = None # 比如 "瀚海·埋骨沙丘"
                
                # 提取那个不是'id'的键，作为结构名
                for k, v in item.items():
                    if k != 'id' and isinstance(v, dict):
                        struct_name = k
                        config = v
                        break
                
                if uid and config:
                    # 如果没有取到结构名，就用uid代替
                    if not struct_name: struct_name = uid
                    processed_list.append((uid, struct_name, config))
                    
        elif isinstance(rooms_data_source, dict):
            for uid, config in rooms_data_source.items():
                processed_list.append((uid, uid, config)) # 字典模式没有额外的结构名

        # =====================================================
        # 第一步：造房 & 建立双重索引
        # =====================================================
        room_cache = {} # 这是一个神奇的缓存，存了ID也存了中文名
        
        self.caller.msg(f"|w开始处理 {filename}...|n")
        
        for uid, struct_name, config in processed_list:
            # 使用 tag 查找，确保唯一性
            found = search_tag(uid, category="batch_room")
            room_key = config.get('key', uid) # 带颜色的名字
            
            if found:
                room = found[0]
                self.caller.msg(f"更新: {uid} / {struct_name}")
            else:
                room = create_object(
                    Room, 
                    key=room_key,
                    tags=[(uid, "batch_room")]
                )
                self.caller.msg(f"创建: {uid}")
            
            # 更新基本属性
            room.key = room_key
            if 'desc' in config: room.db.desc = config['desc']
            if 'name' in config: room.aliases.add(config['name'])
            
            # 存自定义属性
            for k, v in config.items():
                if k not in ['key', 'desc', 'exits', 'name']:
                    setattr(room.db, k, v)
            
            # 【关键修改】：将ID和结构名(中文名)都指向这个房间对象
            # 这样无论 YAML 的 to: 写的是 "gate_001" 还是 "罗刹·金刚媚骨门" 都能找到！
            room_cache[uid] = room
            room_cache[struct_name] = room 

        # =====================================================
        # 第二步：修路 (出口)
        # =====================================================
        count_exits = 0
        for uid, struct_name, config in processed_list:
            src = room_cache.get(uid)
            if not src: continue
            
            for ex_conf in config.get('exits', []):
                direction = ex_conf.get('direction')
                target_str = ex_conf.get('to') # 这里可能是ID，也可能是中文名
                
                # 直接查缓存，因为我们存了两份Key，所以怎么查都有
                target = room_cache.get(target_str)
                
                # 如果缓存里没找到（可能是跨文件的ID），尝试数据库直接查 tag
                if not target:
                    t_found = search_tag(target_str, category="batch_room")
                    if t_found: target = t_found[0]

                if not target:
                    self.caller.msg(f"|r出口错误:|n {struct_name} -> {target_str} (目标不存在)")
                    continue
                
                # 检查出口是否已存在
                found_exit = None
                for ex in src.exits:
                    if ex.key == direction:
                        found_exit = ex
                        break
                
                exit_desc = ex_conf.get('desc', '')
                
                if found_exit:
                    found_exit.destination = target
                    found_exit.db.desc = exit_desc
                else:
                    create_object(
                        Exit, 
                        key=direction, 
                        location=src, 
                        destination=target,
                        attributes=[('desc', exit_desc)]
                    )
                    count_exits += 1
        
        self.caller.msg(f"|g全部完成！检查/连接出口: {count_exits}个|n")

    def _list_files(self):
        try:
            path = os.path.join("data", "rooms")
            if not os.path.exists(path):
                os.makedirs(path)
            files = [f for f in os.listdir(path) if f.endswith('.yaml')]
            self.caller.msg("可用文件: " + ", ".join(files))
        except:
            pass