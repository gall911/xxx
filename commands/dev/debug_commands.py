"""
调试工具命令（完整版 - 包含翻页 + 被动技能 + 详细初始化）
"""
from evennia import Command, search_object
from evennia.utils.evmore import EvMore  # 翻页工具
import json

class CmdDebugGet(Command):
    """查看对象属性"""
    
    key = "xx get"
    aliases = ["xxg"]
    locks = "cmd:perm(Builder)"
    help_category = "开发"
    
    def func(self):
        if not self.args or ' ' not in self.args:
            self.caller.msg("用法: xx get <对象> <属性>")
            return
        
        obj_str, attr_path = self.args.split(None, 1)
        
        if obj_str == "me":
            obj = self.caller
        elif obj_str == "here":
            obj = self.caller.location
        else:
            obj = self.caller.search(obj_str, global_search=True)
            if not obj:
                return
        
        try:
            parts = attr_path.split('.')
            value = obj
            
            for part in parts:
                value = getattr(value, part)
            
            self.caller.msg(f"\n|w{obj.key}.{attr_path}|n")
            self.caller.msg(f"值: |y{value}|n")
            self.caller.msg(f"类型: {type(value).__name__}")
            
            if isinstance(value, (list, dict)):
                try:
                    self.caller.msg(f"详细:\n{json.dumps(value, indent=2, ensure_ascii=False)}")
                except:
                    self.caller.msg(f"详细: {value}")
            
        except AttributeError:
            self.caller.msg(f"|r属性不存在:|n {attr_path}")
        except Exception as e:
            self.caller.msg(f"|r错误:|n {e}")

class CmdDebugSet(Command):
    """设置对象属性"""
    
    key = "xx set"
    aliases = ["xxs"]
    locks = "cmd:perm(Builder)"
    help_category = "开发"
    
    def func(self):
        args = self.args.split(None, 2)
        
        if len(args) < 3:
            self.caller.msg("用法: xx set <对象> <属性> <值>")
            return
        
        obj_str, attr_path, value_str = args
        
        if obj_str == "me":
            obj = self.caller
        elif obj_str == "here":
            obj = self.caller.location
        else:
            obj = self.caller.search(obj_str, global_search=True)
            if not obj:
                return
        
        # 尝试智能转换类型
        try:
            value = eval(value_str)
        except:
            value = value_str
        
        try:
            parts = attr_path.split('.')
            target = obj
            
            for part in parts[:-1]:
                target = getattr(target, part)
            
            setattr(target, parts[-1], value)
            
            self.caller.msg(f"|g成功设置:|n {obj.key}.{attr_path} = {value}")
            
            # 特殊处理：如果改的是 key，自动刷新别名
            if parts[-1] == 'key':
                from evennia.utils.ansi import strip_ansi
                clean = strip_ansi(str(value))
                if clean != str(value): obj.aliases.add(clean)
            
        except Exception as e:
            self.caller.msg(f"|r错误:|n {e}")

class CmdDebugReload(Command):
    """重新加载游戏数据"""
    
    key = "xx reload"
    aliases = ["xxr"]
    locks = "cmd:perm(Builder)"
    help_category = "开发"
    
    def func(self):
        if not self.args:
            self.caller.msg("用法: xx reload <data|config>")
            return
        
        reload_type = self.args.strip().lower()
        
        if reload_type == "data":
            from world.loaders.data_loader import load_all_data
            try:
                load_all_data()
                self.caller.msg("|g游戏数据已重新加载！|n")
            except Exception as e:
                self.caller.msg(f"|r加载失败:|n {e}")
            
        elif reload_type == "config":
            from world.loaders.config_loader import load_all_configs
            try:
                load_all_configs()
                self.caller.msg("|g配置文件已重新加载！|n")
            except Exception as e:
                self.caller.msg(f"|r加载失败:|n {e}")
        else:
            self.caller.msg("未知类型。使用: data 或 config")

class CmdDebugData(Command):
    """查看已加载的游戏数据 (翻页版)"""
    
    key = "xx data"
    aliases = ["xxd"]
    locks = "cmd:perm(Builder)"
    help_category = "开发"
    
    def func(self):
        from world.loaders.game_data import GAME_DATA
        
        if not self.args:
            self.caller.msg("|w" + "=" * 50)
            self.caller.msg("|c游戏数据统计|n")
            self.caller.msg("|w" + "=" * 50)
            for k, v in GAME_DATA.items():
                self.caller.msg(f"{k.capitalize()}: {len(v)} 个")
            self.caller.msg("|w" + "=" * 50)
            return
        
        data_type = self.args.strip().lower()
        
        if data_type not in GAME_DATA:
            self.caller.msg(f"未知数据类型: {data_type}")
            return
        
        data = GAME_DATA[data_type]
        
        # === 使用 EvMore 分页 ===
        lines = []
        lines.append(f"|w=== {data_type.upper()} 数据列表 ({len(data)}) ===|n")
        
        if isinstance(data, dict):
            # 字典类型排序显示
            for key in sorted(data.keys()):
                val = data[key]
                info = ""
                if isinstance(val, dict):
                    if 'name' in val: info = f" - {val['name']}"
                    elif 'key' in val: info = f" - {val['key']}"
                lines.append(f"  |g{key}|n{info}")
        elif isinstance(data, list):
            for item in data:
                lines.append(f"  {item}")
                
        lines.append("|w=== 到底了 ===|n")
        
        EvMore(self.caller, "\n".join(lines))

class CmdQuickInit(Command):
    """快速初始化对象属性（完整版）"""
    
    key = "xx init"
    aliases = ["xxi"]
    locks = "cmd:perm(Builder)"
    help_category = "开发"
    
    def func(self):
        if not self.args:
            target = self.caller
        else:
            target = self.caller.search(self.args.strip())
            if not target:
                return
        
        # 强制初始化所有属性
        target.ndb.hp = 100
        target.ndb.max_hp = 100
        target.ndb.qi = 50
        target.ndb.max_qi = 50
        target.ndb.strength = 10
        target.ndb.agility = 10
        target.ndb.intelligence = 10
        target.ndb.level = 1
        target.ndb.realm = '练气期'
        target.ndb.skills = ['普通攻击']
        target.ndb.passive_skills = []
        target.ndb.dodge_rate = 0.1
        
        self.caller.msg(f"|g已初始化 {target.key}！|n")
        self.caller.msg(f"HP: {target.ndb.hp}/{target.ndb.max_hp}")
        self.caller.msg(f"QI: {target.ndb.qi}/{target.ndb.max_qi}")
        self.caller.msg(f"技能: {target.ndb.skills}")

class CmdAddPassive(Command):
    """添加被动技能（补回来的）"""
    
    key = "xx passive"
    aliases = ["xxp"]
    locks = "cmd:perm(Builder)"
    help_category = "开发"
    
    def func(self):
        if not self.args or ' ' not in self.args:
            self.caller.msg("用法: xx passive <目标> <技能名>")
            self.caller.msg("\n可用被动技能:")
            from world.loaders.game_data import GAME_DATA
            for key, data in GAME_DATA.get('skills', {}).items():
                if data.get('type') == 'passive':
                    self.caller.msg(f"  - {key}")
            return
        
        target_str, skill_name = self.args.split(None, 1)
        
        if target_str == "me":
            target = self.caller
        else:
            target = self.caller.search(target_str)
            if not target:
                return
        
        from world.loaders.game_data import GAME_DATA
        skill_data = GAME_DATA.get('skills', {}).get(skill_name)
        
        if not skill_data:
            self.caller.msg(f"技能不存在: {skill_name}")
            return
        
        if skill_data.get('type') != 'passive':
            self.caller.msg(f"{skill_name} 不是被动技能")
            return
        
        if not hasattr(target.ndb, 'passive_skills') or target.ndb.passive_skills is None:
            target.ndb.passive_skills = []
        
        if skill_name not in target.ndb.passive_skills:
            target.ndb.passive_skills.append(skill_name)
            self.caller.msg(f"|g成功为 {target.key} 添加被动技能: {skill_name}|n")
        else:
            self.caller.msg(f"{target.key} 已拥有 {skill_name}")

class CmdCheckRoom(Command):
    """检查当前房间的真实身份"""
    key = "xx check"
    locks = "cmd:perm(Builder)"
    
    def func(self):
        room = self.caller.location
        self.caller.msg(f"=== 房间诊断报告 ===")
        self.caller.msg(f"Key: {room.key}")
        self.caller.msg(f"ID: #{room.id}")
        self.caller.msg(f"Aliases: {room.aliases.all()}")
        self.caller.msg(f"Tags: {room.tags.all()}")