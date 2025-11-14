from evennia import Command
from typeclasses.spells.loader import load_spell_data

class CmdSkills(Command):
    """
    查看已学技能列表命令
    """
    key = "skills"
    
    def func(self):
        """执行命令"""
        if not hasattr(self.caller.db, 'skills') or not self.caller.db.skills:
            self.caller.msg("你还没有学会任何技能。")
            return
            
        self.caller.msg("你已学会的技能：")
        for skill_key, skill_data in self.caller.db.skills.items():
            spell_data = load_spell_data(skill_key)
            if spell_data:
                level = skill_data.get("level", 1)
                self.caller.msg(f"- {spell_data['name']} (等级 {level}): {spell_data['desc']}")
            else:
                self.caller.msg(f"- {skill_key} (等级 {level})")