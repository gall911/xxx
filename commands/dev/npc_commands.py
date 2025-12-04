"""
NPC管理命令 - 智能配置版
无需额外文件，直接读取内存中的 GAME_DATA
"""
import os
import yaml
from evennia import Command, create_object, search_tag
from evennia.utils.evtable import EvTable
from evennia.utils.ansi import strip_ansi
# 引入全局数据
from world.loaders.game_data import GAME_DATA 

BATCH_TAG_CATEGORY = "batch_code"

# ====================================================
# 1. 列出NPC (xxln) - 修复显示
# ====================================================
class CmdNPCList(Command):
    """
    列出所有NPC
    """
    key = "xx list npc"
    aliases = ["xxln"]
    locks = "cmd:perm(Builder)"
    help_category = "开发"
    
    def func(self):
        from typeclasses.npcs import NPC
        
        npcs = NPC.objects.all().order_by('id')
        if not npcs:
            self.caller.msg("没有找到任何NPC。")
            return
        
        # 优化表格宽度
        table = EvTable("|wID (Key)|n", "|wLv|n", "|wHP|n", "|w位置|n", border="cells")
        
        for npc in npcs:
            # ID处理
            batch_id = ""
            tags = npc.tags.get(category=BATCH_TAG_CATEGORY, return_list=True)
            if tags: batch_id = tags[0]
            display_key = batch_id if batch_id else npc.key
            id_col = f"#{npc.id} ({display_key})"
            
            # 属性读取 (优先内存 -> 数据库 -> 0)
            stats = npc.db.stats or {}
            
            max_hp = getattr(npc.ndb, 'max_hp', stats.get('max_hp', 0))
            hp = getattr(npc.ndb, 'hp', max_hp)
            
            lvl = getattr(npc.ndb, 'level', stats.get('level', 1))
            
            # 位置显示 (显示中文Key)
            loc_name = "无"
            if npc.location:
                loc_name = npc.location.key
            
            table.add_row(id_col, lvl, f"{hp}/{max_hp}", loc_name)
            
        self.caller.msg(table)
        self.caller.msg(f"\n总计: {len(npcs)} 个NPC")

# ====================================================
# 2. 添加单个NPC (xxan) - 智能查字典版
# ====================================================
class CmdNPCAdd(Command):
    """
    创建单个NPC (智能版)
    
    用法:
      xxan <ID>           -> 查配置。如果有配置，自动填名字/属性；没有则创建白板。
      xxan <ID> <中文名>   -> 强制指定中文名，忽略配置名。
    """
    key = "xx add npc"
    aliases = ["xxan"]
    locks = "cmd:perm(Builder)"
    help_category = "开发"
    
    def func(self):
        if not self.args:
            self.caller.msg("用法: xxan <ID> [中文名]")
            return
        
        args = self.args.strip().split(None, 1)
        npc_key = args[0] # 这里是 sony_radio
        
        # === 1. 去 GAME_DATA 查户口 ===
        # data_loader.py 已经把数据加载到 GAME_DATA['npcs'] 里了
        npc_config = GAME_DATA.get('npcs', {}).get(npc_key)
        
        # === 2. 决定名字 ===
        if len(args) > 1:
            # 玩家手动指定了名字: xxan ff 骷髅
            npc_name = args[1]
        elif npc_config:
            # 查到了配置: 用配置里的 name
            npc_name = npc_config.get('name', npc_key)
        else:
            # 啥都没查到: 用 ID 当名字
            npc_name = npc_key

        location = self.caller.location
        
        # === 3. 创建对象 ===
        try:
            new_npc = create_object("typeclasses.npcs.NPC", key=npc_key, location=location)
        except Exception as e:
            self.caller.msg(f"|r创建失败: {e}|n")
            return
        
        # === 4. 设置数据 ===
        new_npc.db.cname = npc_name
        new_npc.db.color_name = npc_name
        
        # 加别名
        clean_name = strip_ansi(npc_name)
        if clean_name != npc_key:
            new_npc.aliases.add(clean_name)
        
        # 填属性
        if npc_config:
            # 有配置，读配置
            stats = npc_config.get('stats', {})
            new_npc.db.stats = stats # 存盘
            
            new_npc.ndb.max_hp = stats.get('max_hp', 100)
            new_npc.ndb.hp = new_npc.ndb.max_hp
            new_npc.ndb.level = stats.get('level', 1)
            
            if 'desc' in npc_config: new_npc.db.desc = npc_config['desc']
            if 'skills' in npc_config: new_npc.db.skills = npc_config['skills']
            if 'drops' in npc_config: new_npc.db.drops = npc_config['drops']
            
            self.caller.msg(f"|g[配置加载成功]|n 已创建: {npc_name}({new_npc.key})")
        else:
            # 没配置，给默认值
            new_npc.ndb.hp = 100
            new_npc.ndb.max_hp = 100
            new_npc.ndb.level = 1
            self.caller.msg(f"|y[无配置模式]|n 已创建: {npc_name}({new_npc.key})")

# ====================================================
# 3. 删除NPC
# ====================================================
class CmdNPCDelete(Command):
    """删除NPC"""
    key = "xx del npc"
    aliases = ["xxdn"]
    locks = "cmd:perm(Builder)"
    help_category = "开发"
    
    def func(self):
        if not self.args:
            self.caller.msg("用法: xxdn <目标>")
            return
        target = self.caller.search(self.args)
        if not target: return
        
        if target.is_typeclass("typeclasses.npcs.NPC"):
            name = target.key
            target.delete()
            self.caller.msg(f"已删除: {name}")
        else:
            self.caller.msg("那个不是NPC。")

# ====================================================
# 4. 批量投放 (保持不变，防止你之前的报错)
# ====================================================
class CmdNPCBatch(Command):
    """全自动批量投放NPC"""
    key = "xx batch npc"
    aliases = ["xxbn"]
    locks = "cmd:perm(Builder)"
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
            self.caller.msg(f"|r找不到文件:|n {file_path}")
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            self.caller.msg(f"|rYAML错误:|n {e}")
            return
        if not data: return

        # 解析数据
        processed_list = []
        raw_items = []
        if isinstance(data, dict):
            if 'npcs' in data:
                npcs = data['npcs']
                if isinstance(npcs, dict): raw_items = list(npcs.items())
                elif isinstance(npcs, list): 
                    for i in npcs: raw_items.append((None, i))
            else:
                raw_items = list(data.items())
        elif isinstance(data, list):
            for i in data: raw_items.append((None, i))
            
        for key, item in raw_items:
            uid = None
            if isinstance(item, dict):
                uid = item.get('key') or item.get('id') or item.get('prototype_key')
                if not uid and key: uid = key
                if not uid:
                    for k, v in item.items():
                        if isinstance(v, dict): uid = k; item = v; break
            if uid and isinstance(item, dict): processed_list.append((str(uid), item))

        self.caller.msg(f"|w识别到 {len(processed_list)} 个NPC配置...|n")
        cnt_create, cnt_update = 0, 0 # 修复之前的解包错误
        
        for uid, config in processed_list:
            loc_key = str(config.get('location') or config.get('location_id')).strip()
            location = self._find_room_unified(loc_key)
            if not location:
                self.caller.msg(f"|y跳过:|n NPC [{uid}] -> 未找到房间 '{loc_key}'")
                continue
            is_unique = config.get('unique', False) or 'boss' in config.get('tags', [])
            npc = None
            if is_unique:
                found = search_tag(uid, category=BATCH_TAG_CATEGORY)
                if found and found[0].is_typeclass("typeclasses.npcs.NPC"):
                    npc = found[0]
                    self.caller.msg(f"更新BOSS: {uid}")
                    cnt_update += 1
            name_str = config.get('name', uid)
            if not npc:
                npc = create_object("typeclasses.npcs.NPC", key=uid, location=location)
                if is_unique: npc.tags.add(uid, category=BATCH_TAG_CATEGORY)
                cnt_create += 1
                self.caller.msg(f"投放: {name_str} |g->|n {location.key}")
            if npc.location != location:
                npc.move_to(location, quiet=True)
                self.caller.msg(f"移动: {name_str} -> {location.key}")
            
            npc.db.cname = name_str
            npc.db.color_name = name_str
            clean_name = strip_ansi(name_str)
            if clean_name != uid: npc.aliases.add(clean_name)
            
            # 属性
            if 'desc' in config: npc.db.desc = config['desc']
            if 'stats' in config:
                npc.db.stats = config['stats']
                npc.ndb.max_hp = config['stats'].get('max_hp', 100)
                npc.ndb.hp = npc.ndb.max_hp
            if 'skills' in config: npc.db.skills = config['skills']
            if 'drops' in config: npc.db.drops = config['drops']
            if hasattr(npc, 'start_chatter'): npc.start_chatter()

        self.caller.msg(f"|g完成! 新增: {cnt_create}, 更新: {cnt_update}|n")

    def _find_room_unified(self, key):
        if not key or key == 'None': return None
        found = search_tag(key, category=BATCH_TAG_CATEGORY)
        if found: 
            if found[0].is_typeclass("typeclasses.rooms.Room"): return found[0]
        found = self.caller.search(key, global_search=True, quiet=True)
        if found:
            if isinstance(found, list): found = found[0]
            if found.is_typeclass("typeclasses.rooms.Room"): return found
        return None

    def _list_files(self):
        try:
            path = os.path.join("data", "npcs")
            if not os.path.exists(path): os.makedirs(path)
            files = [f for f in os.listdir(path) if f.endswith('.yaml')]
            self.caller.msg("可用文件: " + ", ".join(files))
        except: pass