# commands/combat.py
"""战斗相关命令"""
from evennia import Command
from evennia import default_cmds
from world.managers.combat_manager import COMBAT_MANAGER

class CmdAttack(Command):
    """
    攻击目标
    
    用法:
      攻击 <目标>
      attack <target>
    
    开始与目标的战斗。战斗将自动进行，直到一方HP归零。
    """
    
    key = "攻击"
    aliases = ["attack", "att", "fight"]
    locks = "cmd:all()"
    help_category = "战斗"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        if not self.args:
            caller.msg("攻击谁？用法: 攻击 <目标>")
            return
        
        # 查找目标
        target = caller.search(self.args.strip())
        if not target:
            return
        
        # 检查是否是自己
        if target == caller:
            caller.msg("你不能攻击自己！")
            return
        
        # 检查是否已在战斗中
        if hasattr(caller.ndb, 'in_combat') and caller.ndb.in_combat:
            caller.msg("你已经在战斗中了！")
            return
        
        # 检查目标是否可攻击
        if not hasattr(target.ndb, 'hp'):
            caller.msg(f"{target.key} 不能被攻击。")
            return
        
        # 检查是否在安全区
        room = caller.location
        if room and hasattr(room, 'db') and room.db.safe_zone:
            caller.msg("这里是安全区，不能战斗！")
            return
        
        # 开始战斗
        success = COMBAT_MANAGER.start_combat(caller, target)
        
        if not success:
            caller.msg("无法开始战斗。")

class CmdFlee(Command):
    """
    逃离战斗
    
    用法:
      逃跑
      flee
    
    尝试从当前战斗中逃跑。
    """
    
    key = "逃跑"
    aliases = ["flee", "escape", "run"]
    locks = "cmd:all()"
    help_category = "战斗"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        # 检查是否在战斗中
        if not hasattr(caller.ndb, 'in_combat') or not caller.ndb.in_combat:
            caller.msg("你没有在战斗中。")
            return
        
        # TODO: 添加逃跑成功率判定
        import random
        flee_chance = 0.5  # 50%逃跑成功率
        
        if random.random() < flee_chance:
            COMBAT_MANAGER.stop_combat(caller)
            caller.msg("|g你成功逃离了战斗！|n")
        else:
            caller.msg("|r逃跑失败！|n")

class CmdSkills(Command):
    """
    查看技能列表
    
    用法:
      技能
      skills
    
    显示你当前拥有的所有技能。
    """
    
    key = "技能"
    aliases = ["skills", "skill"]
    locks = "cmd:all()"
    help_category = "战斗"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        # 获取技能列表
        skills = getattr(caller.ndb, 'skills', [])
        
        if not skills:
            caller.msg("你还没有学会任何技能。")
            return
        
        from world.loaders.game_data import get_data
        
        # 显示技能列表
        caller.msg("|w" + "=" * 50)
        caller.msg("|c技能列表|n")
        caller.msg("|w" + "=" * 50)
        
        for skill_key in skills:
            skill_data = get_data('skills', skill_key)
            if not skill_data:
                continue
            
            name = skill_data.get('name', skill_key)
            desc = skill_data.get('desc', '无描述')
            cost_qi = skill_data.get('cost_qi', 0)
            cost_hp = skill_data.get('cost_hp', 0)
            cooldown = skill_data.get('cooldown', 0)
            
            caller.msg(f"\n|y{name}|n")
            caller.msg(f"  {desc}")
            
            costs = []
            if cost_qi > 0:
                costs.append(f"灵力: {cost_qi}")
            if cost_hp > 0:
                costs.append(f"生命: {cost_hp}")
            if costs:
                caller.msg(f"  消耗: {', '.join(costs)}")
            
            if cooldown > 0:
                caller.msg(f"  冷却: {cooldown}回合")
        
        caller.msg("|w" + "=" * 50)

class CmdUseSkill(Command):
    """
    在战斗中使用技能
    
    用法:
      施放 <技能名>
      cast <skill>
    
    在战斗中对当前目标使用指定技能。
    """
    
    key = "施放"
    aliases = ["cast", "use"]
    locks = "cmd:all()"
    help_category = "战斗"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        if not self.args:
            caller.msg("使用什么技能？用法: 施放 <技能名>")
            return
        
        # 检查是否在战斗中
        if not hasattr(caller.ndb, 'in_combat') or not caller.ndb.in_combat:
            caller.msg("你不在战斗中。")
            return
        
        skill_name = self.args.strip()
        
        # 查找技能
        from world.loaders.game_data import GAME_DATA
        skill_key = None
        
        for key, skill_data in GAME_DATA['skills'].items():
            if skill_data.get('name') == skill_name or key == skill_name:
                skill_key = key
                break
        
        if not skill_key:
            caller.msg(f"找不到技能: {skill_name}")
            return
        
        # 检查是否拥有该技能
        if skill_key not in getattr(caller.ndb, 'skills', []):
            caller.msg(f"你还没有学会 {skill_name}。")
            return
        
        # 获取目标
        target = getattr(caller.ndb, 'combat_target', None)
        if not target:
            caller.msg("没有战斗目标。")
            return
        
        # 使用技能
        from world.systems.combat_system import CombatSystem
        combat_sys = CombatSystem()
        
        results = combat_sys.use_skill(caller, target, skill_key)
        
        # 显示结果
        for result in results:
            if result.get('message'):
                caller.msg(result['message'])
                if target.has_account:  # 如果目标是玩家
                    target.msg(result['message'])

class CmdStatus(Command):
    """
    查看战斗状态
    
    用法:
      状态
      status
    
    显示你的当前属性和战斗状态。
    """
    
    key = "状态"
    aliases = ["status", "st", "stat"]
    locks = "cmd:all()"
    help_category = "通用"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        caller.msg("|w" + "=" * 50)
        caller.msg(f"|c{caller.key} 的状态|n")
        caller.msg("|w" + "=" * 50)
        
        # 基础属性
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
        
        # 战斗属性
        strength = getattr(caller.ndb, 'strength', 10)
        agility = getattr(caller.ndb, 'agility', 10)
        intelligence = getattr(caller.ndb, 'intelligence', 10)
        
        caller.msg(f"\n力量: |y{strength}|n  敏捷: |y{agility}|n  智力: |y{intelligence}|n")
        
        # 战斗状态
        if hasattr(caller.ndb, 'in_combat') and caller.ndb.in_combat:
            target = getattr(caller.ndb, 'combat_target', None)
            if target:
                caller.msg(f"\n|r【战斗中】|n 目标: {target.key}")
        
        # Buff/Debuff
        buffs = getattr(caller.ndb, 'buffs', [])
        debuffs = getattr(caller.ndb, 'debuffs', [])
        
        if buffs:
            caller.msg("\n|g增益效果:|n")
            for buff in buffs:
                attr = buff['attribute']
                value = buff['value']
                remaining = buff['remaining']
                caller.msg(f"  {attr} +{value} (剩余{remaining}回合)")
        
        if debuffs:
            caller.msg("\n|r减益效果:|n")
            for debuff in debuffs:
                attr = debuff['attribute']
                value = debuff['value']
                remaining = debuff['remaining']
                caller.msg(f"  {attr} -{value} (剩余{remaining}回合)")
        
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
        """添加命令到命令集"""
        super().at_cmdset_creation()
        
        self.add(CmdAttack())
        self.add(CmdFlee())
        self.add(CmdSkills())
        self.add(CmdUseSkill())
        self.add(CmdStatus())