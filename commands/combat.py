# commands/combat.py
"""战斗相关命令（简化版）"""
from evennia import Command, default_cmds
from world.managers.combat_manager import COMBAT_MANAGER

class CmdAttack(Command):
    """
    攻击目标
    
    用法:
      攻击 <目标>
      attack <target>
    """
    
    key = "攻击"
    aliases = ["attack", "att"]
    locks = "cmd:all()"
    help_category = "战斗"
    
    def func(self):
        caller = self.caller
        
        if not self.args:
            caller.msg("攻击谁？用法: 攻击 <目标>")
            return
        
        target = caller.search(self.args.strip())
        if not target:
            return
        
        if target == caller:
            caller.msg("你不能攻击自己！")
            return
        
        if hasattr(caller.ndb, 'in_combat') and caller.ndb.in_combat:
            caller.msg("你已经在战斗中了！")
            return
        
        if not hasattr(target.ndb, 'hp'):
            caller.msg(f"{target.key} 不能被攻击。")
            return
        
        room = caller.location
        if room and hasattr(room, 'db') and room.db.safe_zone:
            caller.msg("这里是安全区，不能战斗！")
            return
        
        COMBAT_MANAGER.start_combat(caller, target)

class CmdFlee(Command):
    """
    逃离战斗
    
    用法:
      逃跑
      flee
    """
    
    key = "逃跑"
    aliases = ["flee", "escape"]
    locks = "cmd:all()"
    help_category = "战斗"
    
    def func(self):
        caller = self.caller
        
        if not hasattr(caller.ndb, 'in_combat') or not caller.ndb.in_combat:
            caller.msg("你没有在战斗中。")
            return
        
        import random
        flee_chance = 0.5
        
        if random.random() < flee_chance:
            COMBAT_MANAGER.stop_combat(caller)
            caller.msg("|g你成功逃离了战斗！|n")
        else:
            caller.msg("|r逃跑失败！|n")

class CmdStatus(Command):
    """
    查看战斗状态
    
    用法:
      状态
      status
    """
    
    key = "状态"
    aliases = ["status", "st"]
    locks = "cmd:all()"
    help_category = "通用"
    
    def func(self):
        caller = self.caller
        
        caller.msg("|w" + "=" * 50)
        caller.msg(f"|c{caller.key} 的状态|n")
        caller.msg("|w" + "=" * 50)
        
        hp = getattr(caller.ndb, 'hp', 0)
        max_hp = getattr(caller.ndb, 'max_hp', 100)
        qi = getattr(caller.ndb, 'qi', 0)
        max_qi = getattr(caller.ndb, 'max_qi', 50)
        level = getattr(caller.ndb, 'level', 1)
        realm = getattr(caller.ndb, 'realm', '练气期')
        
        hp_bar = self._create_bar(hp, max_hp, 20, '|r', '|w')
        qi_bar = self._create_bar(qi, max_qi, 20, '|c', '|w')
        
        caller.msg(f"\n境界: |y{realm}|n  等级: |y{level}|n")
        caller.msg(f"生命: {hp_bar} |w{hp}/{max_hp}|n")
        caller.msg(f"灵力: {qi_bar} |w{qi}/{max_qi}|n")
        
        strength = getattr(caller.ndb, 'strength', 10)
        agility = getattr(caller.ndb, 'agility', 10)
        intelligence = getattr(caller.ndb, 'intelligence', 10)
        
        caller.msg(f"\n力量: |y{strength}|n  敏捷: |y{agility}|n  智力: |y{intelligence}|n")
        
        if hasattr(caller.ndb, 'in_combat') and caller.ndb.in_combat:
            target = getattr(caller.ndb, 'combat_target', None)
            if target:
                caller.msg(f"\n|r【战斗中】|n 目标: {target.key}")
        
        caller.msg("|w" + "=" * 50)
    
    def _create_bar(self, current, maximum, length, filled_color, empty_color):
        """创建进度条"""
        if maximum == 0:
            filled = 0
        else:
            filled = int((current / maximum) * length)
        
        empty = length - filled
        bar = filled_color + "█" * filled + empty_color + "░" * empty + "|n"
        return bar

# 命令集
class CombatCmdSet(default_cmds.CharacterCmdSet):
    """战斗命令集"""
    
    key = "CombatCmdSet"
    
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        
        self.add(CmdAttack())
        self.add(CmdFlee())
        self.add(CmdStatus())