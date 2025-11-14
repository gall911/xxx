from evennia import Command
from typeclasses.spells.loader import load_spell_data, get_spell_key_by_name

class CmdSkillLearn(Command):
    """
    学习技能命令
    """
    key = "learn"
    
    def func(self):
        """执行命令"""
        skill_input = self.args.strip()
        if not skill_input:
            self.caller.msg("学习什么技能？")
            return
            
        # 尝试通过输入获取技能键名
        # 首先假设输入是技能键名
        spell_key = skill_input
        spell_data = load_spell_data(spell_key)
        
        # 如果没找到，则尝试通过技能名称查找键名
        if not spell_data:
            spell_key = get_spell_key_by_name(skill_input)
            if spell_key:
                spell_data = load_spell_data(spell_key)
        
        if not spell_data:
            self.caller.msg(f"找不到技能：{skill_input}")
            return
            
        # 初始化技能字典（如果不存在）
        if not self.caller.db.skills:
            self.caller.db.skills = {}
            
        # 添加技能，默认1级
        self.caller.db.skills[spell_key] = {"level": 1}
        self.caller.msg(f"你学会了技能：{spell_data['name']}")