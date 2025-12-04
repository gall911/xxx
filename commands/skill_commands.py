# commands/skill_commands.py
"""技能管理命令（独立文件）"""
from evennia import Command, default_cmds
from world.loaders.game_data import get_data, GAME_DATA
from world.loaders.skill_loader import get_skill_at_level

class CmdSkills(Command):
    """
    查看已学会的技能
    
    用法:
      skills              - 查看所有已学会的技能
      skills <技能key>    - 查看技能详情
    
    示例:
      skills
      skills fireball
    """
    
    key = "skills"
    aliases = ["技能"]
    locks = "cmd:all()"
    help_category = "技能"
    
    def func(self):
        if not self.args:
            self._list_skills()
        else:
            self._show_skill_detail(self.args.strip())
    
    def _list_skills(self):
        """列出所有已学会的技能"""
        learned = self.caller.db.learned_skills or {}
        
        if not learned:
            self.caller.msg("|y你还没有学会任何技能。|n")
            return
        
        self.caller.msg("|w=== 已学会的技能 ===|n")
        
        for skill_key, level in learned.items():
            skill_data = get_data('skills', skill_key)
            if not skill_data:
                continue
            
            name = skill_data.get('name', skill_key)
            skill_type = skill_data.get('type', 'unknown')
            type_str = "|g被动|n" if skill_type == 'passive' else "|c主动|n"
            max_level = skill_data.get('level_formula', {}).get('max_level', 1)
            
            self.caller.msg(f"  [{type_str}] {name} Lv{level}/{max_level} - {skill_key}")
        
        self.caller.msg("\n使用 'skills <key>' 查看详情")
        self.caller.msg("使用 'equip <槽位> <key>' 装备技能")
    
    def _show_skill_detail(self, skill_key):
        """显示技能详情"""
        if skill_key not in self.caller.db.learned_skills:
            self.caller.msg(f"|r你还没学会 {skill_key}！|n")
            return
        
        level = self.caller.db.learned_skills[skill_key]
        skill_config = get_skill_at_level(skill_key, level)
        
        if not skill_config:
            self.caller.msg("|r找不到技能配置！|n")
            return
        
        name = skill_config.get('name', skill_key)
        desc = skill_config.get('desc', '无描述')
        skill_type = skill_config.get('type', 'unknown')
        
        self.caller.msg(f"|w=== {name} Lv{level} ===|n")
        self.caller.msg(f"|y{desc}|n\n")
        self.caller.msg(f"类型: {skill_type}")
        self.caller.msg(f"元素: {skill_config.get('element', 'none')}")
        
        if skill_type == 'active':
            cast_time = skill_config.get('cast_time', 0)
            cooldown = skill_config.get('cooldown', 0)
            cost_qi = skill_config.get('cost_qi', 0)
            damage = skill_config.get('damage', 0)
            accuracy = skill_config.get('accuracy', 0)
            
            self.caller.msg(f"施法时间: {cast_time}秒")
            self.caller.msg(f"冷却时间: {cooldown}回合")
            self.caller.msg(f"消耗灵力: {cost_qi}")
            self.caller.msg(f"基础伤害: {damage}")
            self.caller.msg(f"命中率: {accuracy*100}%")

class CmdLearnSkill(Command):
    """
    学习技能
    
    用法:
      learn <技能key>
    
    示例:
      learn fireball
      learn counter_mastery
    """
    
    key = "learn"
    aliases = ["学习"]
    locks = "cmd:all()"
    help_category = "技能"
    
    def func(self):
        if not self.args:
            self.caller.msg("用法: learn <技能key>")
            return
        
        skill_key = self.args.strip()
        
        # 检查技能是否存在
        skill_data = get_data('skills', skill_key)
        if not skill_data:
            self.caller.msg(f"|r找不到技能: {skill_key}|n")
            return
        
        # 检查是否已学会
        if skill_key in (self.caller.db.learned_skills or {}):
            self.caller.msg(f"|y你已经学会了 {skill_data['name']}！|n")
            return
        
        # 检查学习条件
        # TODO: 检查境界、等级、前置技能
        
        # 学习技能
        if not hasattr(self.caller.db, 'learned_skills'):
            self.caller.db.learned_skills = {}
        
        self.caller.db.learned_skills[skill_key] = 1
        self.caller.msg(f"|g你学会了 {skill_data['name']} Lv1！|n")

class CmdUpgradeSkill(Command):
    """
    升级技能
    
    用法:
      upgrade <技能key>
    
    示例:
      upgrade fireball
    """
    
    key = "upgrade"
    aliases = ["升级技能"]
    locks = "cmd:all()"
    help_category = "技能"
    
    def func(self):
        if not self.args:
            self.caller.msg("用法: upgrade <技能key>")
            return
        
        skill_key = self.args.strip()
        learned = self.caller.db.learned_skills or {}
        
        if skill_key not in learned:
            self.caller.msg(f"|r你还没学会 {skill_key}！|n")
            return
        
        current_level = learned[skill_key]
        skill_data = get_data('skills', skill_key)
        max_level = skill_data.get('level_formula', {}).get('max_level', 1)
        
        if current_level >= max_level:
            self.caller.msg(f"|y{skill_data['name']} 已经满级！|n")
            return
        
        # TODO: 检查升级条件（消耗物品/金币/经验）
        
        self.caller.db.learned_skills[skill_key] += 1
        new_level = self.caller.db.learned_skills[skill_key]
        
        self.caller.msg(f"|g{skill_data['name']} 升级到 Lv{new_level}！|n")

class CmdEquipSkill(Command):
    """
    装备技能到技能槽
    
    用法:
      equip                        - 查看已装备的技能
      equip <槽位> <技能key>       - 装备技能
    
    槽位类型:
      inner         - 内功心法槽（被动）
      movement      - 身法槽（被动）
      attack1       - 攻击技能槽1（主动）
      attack2       - 攻击技能槽2（主动）
    
    示例:
      equip
      equip inner counter_mastery
      equip attack1 fireball
    """
    
    key = "equip"
    aliases = ["装备技能"]
    locks = "cmd:all()"
    help_category = "技能"
    
    def func(self):
        if not self.args:
            self._show_equipped()
            return
        
        args = self.args.split()
        if len(args) != 2:
            self.caller.msg("用法: equip <槽位> <技能key>")
            return
        
        slot_name, skill_key = args
        
        # 初始化技能槽
        if not hasattr(self.caller.db, 'skill_slots'):
            self.caller.db.skill_slots = {
                'inner': None,
                'movement': None,
                'attack1': None,
                'attack2': None,
            }
        
        # 检查槽位
        if slot_name not in self.caller.db.skill_slots:
            self.caller.msg(f"|r不存在槽位: {slot_name}|n")
            return
        
        # 检查是否学会
        if skill_key not in (self.caller.db.learned_skills or {}):
            self.caller.msg(f"|r你还没学会 {skill_key}！|n")
            return
        
        # 检查类型匹配
        skill_data = get_data('skills', skill_key)
        skill_type = skill_data.get('type')
        
        if slot_name in ['inner', 'movement'] and skill_type != 'passive':
            self.caller.msg("|r这个槽位只能装备被动技能！|n")
            return
        
        if slot_name.startswith('attack') and skill_type != 'active':
            self.caller.msg("|r这个槽位只能装备主动技能！|n")
            return
        
        # 装备技能
        old_skill = self.caller.db.skill_slots.get(slot_name)
        self.caller.db.skill_slots[slot_name] = skill_key
        
        if old_skill:
            old_data = get_data('skills', old_skill)
            self.caller.msg(f"|y卸下了 {old_data['name']}|n")
        
        self.caller.msg(f"|g装备了 {skill_data['name']} 到 {slot_name}！|n")
        
        # TODO: 应用被动技能效果
    
    def _show_equipped(self):
        """显示已装备的技能"""
        self.caller.msg("|w=== 已装备的技能 ===|n")
        
        slots = self.caller.db.skill_slots or {
            'inner': None,
            'movement': None,
            'attack1': None,
            'attack2': None,
        }
        
        slot_names = {
            'inner': '内功心法槽',
            'movement': '身法槽',
            'attack1': '攻击技能槽1',
            'attack2': '攻击技能槽2',
        }
        
        for slot_key, slot_name in slot_names.items():
            skill_key = slots.get(slot_key)
            
            if skill_key:
                skill_data = get_data('skills', skill_key)
                level = self.caller.db.learned_skills.get(skill_key, 1)
                name = skill_data.get('name', skill_key)
                self.caller.msg(f"  {slot_name}: {name} Lv{level}")
            else:
                self.caller.msg(f"  {slot_name}: |r空|n")

# 命令集
class SkillCmdSet(default_cmds.CharacterCmdSet):
    """技能命令集"""
    
    key = "SkillCmdSet"
    
    def at_cmdset_creation(self):
        super().at_cmdset_creation()
        
        self.add(CmdSkills())
        self.add(CmdLearnSkill())
        self.add(CmdUpgradeSkill())
        self.add(CmdEquipSkill())