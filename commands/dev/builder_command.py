#/commands/dev/builder_command.py
"""
建造者命令 - 用YAML数据创建游戏对象
"""
from evennia import Command, create_object
from world.loaders.game_data import GAME_DATA
from typeclasses.npcs import NPC
from typeclasses.rooms import Room

class CmdSpawnNPC(Command):
    """
    从YAML数据生成NPC
    
    用法:
      @spawn npc <NPC配置名>
      @spawn npc <NPC配置名> = <自定义key>
    
    例子:
      @spawn npc 村长
      @spawn npc 野猪 = 野猪王
    """
    
    key = "@spawn"
    aliases = ["@生成"]
    locks = "cmd:perm(Builder)"
    help_category = "建造"
    
    def func(self):
        if not self.args:
            self.caller.msg("用法: @spawn npc <NPC名>")
            return
        
        # 解析参数
        parts = self.args.strip().split(None, 1)
        if len(parts) < 2:
            self.caller.msg("用法: @spawn npc <NPC名>")
            return
        
        obj_type = parts[0].lower()
        rest = parts[1]
        
        # 检查是否有自定义key
        if "=" in rest:
            npc_name, custom_key = rest.split("=", 1)
            npc_name = npc_name.strip()
            custom_key = custom_key.strip()
        else:
            npc_name = rest.strip()
            custom_key = npc_name
        
        if obj_type == "npc":
            self._spawn_npc(npc_name, custom_key)
        else:
            self.caller.msg(f"未知类型: {obj_type}")
    
    def _spawn_npc(self, npc_name, custom_key):
        """生成NPC"""
        # 从YAML数据查找
        npc_data = GAME_DATA['npcs'].get(npc_name)
        
        if not npc_data:
            self.caller.msg(f"|r未找到NPC配置: {npc_name}|n")
            self.caller.msg(f"|y可用NPC: {', '.join(list(GAME_DATA['npcs'].keys())[:5])}...|n")
            return
        
        # 创建NPC对象
        npc = create_object(
            typeclass="typeclasses.npcs.NPC",
            key=custom_key,
            location=self.caller.location
        )
        
        # 设置属性
        npc.db.desc = npc_data.get('desc', f"这是 {custom_key}")
        npc.db.stats = npc_data.get('stats', {})
        npc.db.skills = npc_data.get('skills', ['普通攻击'])
        npc.db.passive_skills = npc_data.get('passive_skills', [])
        npc.db.drops = npc_data.get('drops', [])
        npc.db.dialogue = npc_data.get('dialogue', f"{custom_key}: 你好。")
        npc.db.ai_type = npc_data.get('ai_type', 'passive')
        
        # 初始化NDB属性
        npc._init_ndb_attributes()
        
        # 显示信息
        self.caller.msg(f"|g成功创建NPC: {custom_key}|n")
        self.caller.msg(f"  配置: {npc_name}")
        self.caller.msg(f"  等级: {npc.ndb.level}")
        self.caller.msg(f"  生命: {npc.ndb.max_hp}")
        self.caller.msg(f"  技能: {', '.join(npc.db.skills)}")


class CmdSpawnRoom(Command):
    """
    从YAML数据生成房间
    
    用法:
      @spawnroom <房间配置名>
    
    例子:
      @spawnroom 新手村_广场
    """
    
    key = "@spawnroom"
    aliases = ["@生成房间"]
    locks = "cmd:perm(Builder)"
    help_category = "建造"
    
    def func(self):
        if not self.args:
            self.caller.msg("用法: @spawnroom <房间名>")
            self.caller.msg(f"|y可用房间: {', '.join(list(GAME_DATA['rooms'].keys())[:5])}...|n")
            return
        
        room_name = self.args.strip()
        room_data = GAME_DATA['rooms'].get(room_name)
        
        if not room_data:
            self.caller.msg(f"|r未找到房间配置: {room_name}|n")
            self.caller.msg(f"|y可用房间: {', '.join(list(GAME_DATA['rooms'].keys())[:5])}...|n")
            return
        
        # 创建房间
        room = create_object(
            typeclass="typeclasses.rooms.Room",
            key=room_data.get('key', room_name)
        )
        
        # 设置属性
        room.db.desc = room_data.get('desc', '这是一个普通的房间。')
        room.db.room_type = room_data.get('type', 'normal')
        
        self.caller.msg(f"|g成功创建房间: {room.key}|n")
        self.caller.msg(f"  配置: {room_name}")


class CmdQuickNPC(Command):
    """
    快速创建测试NPC (不需要YAML配置)
    
    用法:
      @qnpc <名字>
      @qnpc <名字> <等级>
    
    例子:
      @qnpc 村长
      @qnpc 野猪 5
    """
    
    key = "@qnpc"
    aliases = ["@快速npc"]
    locks = "cmd:perm(Builder)"
    help_category = "建造"
    
    def func(self):
        if not self.args:
            self.caller.msg("用法: @qnpc <名字> [等级]")
            return
        
        parts = self.args.strip().split()
        npc_name = parts[0]
        level = int(parts[1]) if len(parts) > 1 else 1
        
        # 创建NPC
        npc = create_object(
            typeclass="typeclasses.npcs.NPC",
            key=npc_name,
            location=self.caller.location
        )
        
        # 设置基础属性
        npc.db.desc = f"一个等级{level}的 {npc_name}"
        npc.db.stats = {
            'level': level,
            'max_hp': 100 * level,
            'max_qi': 50 * level,
            'strength': 10 + level * 2,
            'agility': 10 + level * 2
        }
        npc.db.skills = ['普通攻击']
        npc.db.dialogue = f"{npc_name}: 你好,旅行者。"
        
        # 初始化
        npc._init_ndb_attributes()
        
        self.caller.msg(f"|g创建成功: {npc_name} (Lv.{level})|n")


class CmdListData(Command):
    """
    列出YAML数据
    
    用法:
      @listdata npcs      - 列出所有NPC
      @listdata rooms     - 列出所有房间
      @listdata quests    - 列出所有任务
      @listdata items     - 列出所有物品
    """
    
    key = "@listdata"
    aliases = ["@数据列表"]
    locks = "cmd:perm(Builder)"
    help_category = "建造"
    
    def func(self):
        if not self.args:
            self.caller.msg("用法: @listdata <npcs|rooms|quests|items>")
            return
        
        data_type = self.args.strip().lower()
        
        if data_type not in GAME_DATA:
            self.caller.msg(f"|r未知数据类型: {data_type}|n")
            self.caller.msg(f"|y可用类型: {', '.join(GAME_DATA.keys())}|n")
            return
        
        data = GAME_DATA[data_type]
        
        self.caller.msg(f"\n|c{'=' * 60}|n")
        self.caller.msg(f"|c{data_type.upper()} 数据列表|n")
        self.caller.msg(f"|c{'=' * 60}|n")
        
        for i, (key, value) in enumerate(data.items(), 1):
            name = value.get('name', key) if isinstance(value, dict) else key
            self.caller.msg(f"{i:3}. {key:30} {name}")
            
            if i >= 50:  # 限制显示数量
                remaining = len(data) - 50
                if remaining > 0:
                    self.caller.msg(f"... 还有 {remaining} 个")
                break
        
        self.caller.msg(f"|c{'=' * 60}|n")
        self.caller.msg(f"总计: {len(data)} 个\n")


class CmdShowData(Command):
    """
    查看YAML数据详情
    
    用法:
      @showdata npc <NPC名>
      @showdata quest <任务名>
    
    例子:
      @showdata npc 村长
      @showdata quest 新手试炼_1
    """
    
    key = "@showdata"
    aliases = ["@查看数据"]
    locks = "cmd:perm(Builder)"
    help_category = "建造"
    
    def func(self):
        if not self.args or " " not in self.args:
            self.caller.msg("用法: @showdata <类型> <名字>")
            self.caller.msg("类型: npc, quest, item, room, skill")
            return
        
        parts = self.args.strip().split(None, 1)
        data_type = parts[0].lower()
        name = parts[1]
        
        # 映射类型到数据key
        type_map = {
            'npc': 'npcs',
            'quest': 'quests',
            'item': 'items',
            'room': 'rooms',
            'skill': 'skills'
        }
        
        data_key = type_map.get(data_type)
        if not data_key:
            self.caller.msg(f"|r未知类型: {data_type}|n")
            return
        
        data = GAME_DATA[data_key].get(name)
        
        if not data:
            self.caller.msg(f"|r未找到: {name}|n")
            return
        
        # 显示详情
        import json
        self.caller.msg(f"\n|c{'=' * 60}|n")
        self.caller.msg(f"|c{data_type.upper()}: {name}|n")
        self.caller.msg(f"|c{'=' * 60}|n")
        self.caller.msg(json.dumps(data, indent=2, ensure_ascii=False))
        self.caller.msg(f"|c{'=' * 60}|n\n")