"""
房间管理命令 - 翻页终极版
1. xxlr 支持翻页 (EvMore)，不再刷屏
2. xxbr 保持原样 (显示中文名 + 自动出口逻辑)
"""
import os
import sys
import yaml
from evennia import Command, create_object, search_tag
from evennia.utils.evmore import EvMore  # 引入翻页工具
from typeclasses.rooms import Room

# 安全获取Exit类
def get_exit_class_safe():
    if "typeclasses.exits" in sys.modules:
        try: return sys.modules["typeclasses.exits"].Exit
        except AttributeError: pass
    try:
        from typeclasses.exits import Exit
        return Exit
    except Exception:
        from evennia import DefaultExit
        return DefaultExit

BATCH_TAG_CATEGORY = "batch_code"

# =============================================================
# 1. 列表命令 (已集成 EvMore 分页)
# =============================================================
class CmdRoomList(Command):
    """
    列出所有房间 (带翻页)
    """
    key = "xx list room"
    aliases = ["xxlr"]
    locks = "cmd:perm(Builder)"
    help_category = "开发"
    
    def func(self):
        rooms = Room.objects.all().order_by('id')
        if not rooms:
            self.caller.msg("没有找到任何房间。")
            return
        
        count = len(rooms)
        
        # === 核心修改：准备一个列表来存所有行 ===
        lines = []
        lines.append(f"|w=== 房间列表 ({count}) ===|n")
        
        for room in rooms:
            # 1. 获取 Batch ID
            uid = ""
            tags = room.tags.get(category=BATCH_TAG_CATEGORY, return_list=True)
            if tags:
                uid = tags[0]
            if not uid:
                aliases = room.aliases.all()
                if aliases: uid = aliases[0]
            
            batch_id_str = f"|g[{uid}]|n" if uid else ""
            
            # 2. 构造点击链接
            cmd = f"@tel #{room.id}"
            clickable_name = f"|lc{cmd}|lt{room.key}|le"
            
            # 3. 把这一行加到列表里 (而不是直接发)
            line = f"|w(#{room.id})|n {clickable_name} {batch_id_str}"
            lines.append(line)
            
        lines.append("|w=== 到底了 ===|n")

        # === 最后：把列表交给 EvMore 处理 ===
        # 它会自动分页，回车下一页，q 退出
        EvMore(self.caller, "\n".join(lines))

# =============================================================
# 2. 批量生成命令 (保持不变)
# =============================================================
class CmdRoomBatch(Command):
    """
    全自动批量创建/更新房间与出口
    """
    key = "xx batch room"
    aliases = ["xxbr"]
    locks = "cmd:perm(Builder)"
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
            self.caller.msg(f"|r找不到文件:|n {file_path}")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            self.caller.msg(f"|rYAML读取错误:|n {e}")
            return

        rooms_data_source = data.get('rooms')
        if not rooms_data_source: return

        processed_list = []
        if isinstance(rooms_data_source, list):
            for item in rooms_data_source:
                uid = item.get('id')
                config = next((v for k, v in item.items() if isinstance(v, dict)), {})
                struct_name = next((k for k, v in item.items() if isinstance(v, dict)), uid)
                if uid: processed_list.append((str(uid), struct_name, config))     
        elif isinstance(rooms_data_source, dict):
            for uid, config in rooms_data_source.items():
                processed_list.append((str(uid), str(uid), config))

        room_cache = {} 
        self.caller.msg(f"|w开始处理 {filename}...|n")
        
        for uid, struct_name, config in processed_list:
            found = search_tag(uid, category=BATCH_TAG_CATEGORY)
            if not found:
                found = self.caller.search(uid, global_search=True, quiet=True)
            
            room_key = config.get('key', uid)
            
            if found:
                room = found[0]
                self.caller.msg(f"更新: {uid} ({room_key})")
            else:
                room = create_object(Room, key=room_key)
                self.caller.msg(f"创建: {uid} ({room_key})")
            
            room.tags.add(uid, category=BATCH_TAG_CATEGORY)
            room.aliases.add(uid)
            if 'name' in config: room.aliases.add(config['name'])
            
            room.key = room_key
            if 'desc' in config: room.db.desc = config['desc']
            for k, v in config.items():
                if k not in ['key', 'desc', 'exits', 'name', 'id']:
                    setattr(room.db, k, v)
            
            room_cache[uid] = room
            room_cache[struct_name] = room 

        count_exits_created = 0
        count_exits_updated = 0
        ExitClass = get_exit_class_safe()
        
        for uid, struct_name, config in processed_list:
            src = room_cache.get(uid)
            if not src: continue
            
            for ex_conf in config.get('exits', []):
                direction = ex_conf.get('direction')
                target_str = str(ex_conf.get('to'))
                
                target = room_cache.get(target_str)
                if not target:
                    t_found = search_tag(target_str, category=BATCH_TAG_CATEGORY)
                    if not t_found:
                        t_found = self.caller.search(target_str, global_search=True, quiet=True)
                    if t_found: target = t_found[0]

                if not target: continue
                
                found_exit = None
                for ex in src.exits:
                    if ex.key == direction:
                        found_exit = ex
                        break
                
                exit_desc = ex_conf.get('desc', '')
                if found_exit:
                    if found_exit.destination != target:
                        found_exit.destination = target
                    found_exit.db.desc = exit_desc
                    count_exits_updated += 1
                else:
                    create_object(
                        ExitClass, 
                        key=direction, 
                        location=src, 
                        destination=target,
                        attributes=[('desc', exit_desc)]
                    )
                    count_exits_created += 1
        
        self.caller.msg(f"|g全部完成！新建出口: {count_exits_created}, 更新/检查出口: {count_exits_updated}|n")

    def _list_files(self):
        try:
            path = os.path.join("data", "rooms")
            if not os.path.exists(path): os.makedirs(path)
            files = [f for f in os.listdir(path) if f.endswith('.yaml')]
            self.caller.msg("可用文件: " + ", ".join(files))
        except: pass