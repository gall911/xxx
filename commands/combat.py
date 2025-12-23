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

from evennia import Command
# 引入你刚才发的加载器
from world.loaders.attr_loader import AttrLoader 

# commands/combat.py
# 修复版 CmdStatus - 统一数据源

from world.systems.attr_manager import AttrManager
from world.const import At


class CmdStatus(Command):
    """
    查看战斗状态
    
    用法:
      状态 (st)
    """
    key = "状态"
    aliases = ["status", "st"]
    locks = "cmd:all()"
    help_category = "通用"
    
    def func(self):
        caller = self.caller
        
        # 🔥 关键修复: 先强制同步,确保 ndb 是最新的
        if hasattr(caller, 'sync_stats_to_ndb'):
            caller.sync_stats_to_ndb()
        
        # 1. 动态获取属性显示名
        hp_name = AttrManager.get_name(At.HP)
        qi_name = AttrManager.get_name(At.QI)
        str_name = AttrManager.get_name(At.STRENGTH)
        agi_name = AttrManager.get_name(At.AGILITY)
        int_name = AttrManager.get_name(At.INTELLIGENCE)
        con_name = AttrManager.get_name(At.CONSTITUTION)
        
        # 2. 🔥 从 db 读取权威数据 (境界、等级)
        realm = caller.db.realm or '未知'
        level = caller.db.level or 1
        
        # 3. 🔥 从 ndb 读取战斗数据 (含装备加成)
        hp = getattr(caller.ndb, At.HP, 0)
        max_hp = getattr(caller.ndb, At.MAX_HP, 100)
        qi = getattr(caller.ndb, At.QI, 0)
        max_qi = getattr(caller.ndb, At.MAX_QI, 50)
        
        strength = getattr(caller.ndb, At.STRENGTH, 10)
        agility = getattr(caller.ndb, At.AGILITY, 10)
        intelligence = getattr(caller.ndb, At.INTELLIGENCE, 10)
        constitution = getattr(caller.ndb, At.CONSTITUTION, 10)
        
        # 4. 绘制界面
        caller.msg("|c" + "=" * 50 + "|n")
        caller.msg(f"|y{caller.key}|n 的个人状态")
        caller.msg("|c" + "-" * 50 + "|n")
        
        # 进度条
        hp_bar = self._create_bar(hp, max_hp, 30, '|r', '|x')
        qi_bar = self._create_bar(qi, max_qi, 30, '|c', '|x')
        
        # 🔥 境界和等级从 db 读
        caller.msg(f"境界: |g{realm}|n   等级: |g{level}|n")
        caller.msg(f"{hp_name}: {hp_bar} |w{hp}/{max_hp}|n")
        caller.msg(f"{qi_name}: {qi_bar} |w{qi}/{max_qi}|n")
        caller.msg("")
        
        # 属性显示
        caller.msg(f"|w[基础属性]|n")
        caller.msg(f"  {str_name}: |y{strength:<5}|n {agi_name}: |y{agility:<5}|n")
        caller.msg(f"  {int_name}: |y{intelligence:<5}|n {con_name}: |y{constitution:<5}|n")
        
        # 战斗状态
        if hasattr(caller.ndb, 'in_combat') and caller.ndb.in_combat:
            target = getattr(caller.ndb, 'combat_target', None)
            if target:
                caller.msg(f"\n|r【战斗中】|n 目标: {target.key}")
        
        caller.msg("|c" + "=" * 50 + "|n")
    
    def _create_bar(self, current, maximum, length, filled_color, empty_color):
        """创建进度条"""
        if maximum == 0:
            pct = 0
        else:
            pct = max(0, min(1, current / maximum))
        
        filled = int(pct * length)
        empty = length - filled
        return f"{filled_color}{'█' * filled}{empty_color}{'░' * empty}|n"

# 命令集
class CombatCmdSet(default_cmds.CharacterCmdSet):
    """战斗命令集"""
    
    key = "CombatCmdSet"
    
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        
        self.add(CmdAttack())
        self.add(CmdFlee())
        self.add(CmdStatus())