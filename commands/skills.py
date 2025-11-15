from evennia import Command
from typeclasses.spells.loader import load_spell_data
from typeclasses.spells.loader import load_spell_data, MAGIC_INDEX
class CmdSkills(Command):
    """
    查看已学技能列表命令
    """
    key = "skills"
    
    def func(self):
        """执行命令"""
        if not hasattr(self.caller.db, 'skills') or not self.caller.db.skills:
            self.caller.msg("|m你还没有学会任何技能。|n")
            return
            
        self.caller.msg("|m你已学会的技能：|n")
        for skill_key, skill_data in self.caller.db.skills.items():
            level = skill_data.get("level", 1)
            try:
                # 直接加载法术数据（现在每个文件都包含完整的法术定义）
                spell_data = load_spell_data(skill_key)
                
                if spell_data and 'name' in spell_data:
                    # 只显示技能键名的最后一部分（例如 fire.fb 显示为 fb）
                    display_key = skill_key.split(".")[-1] if "." in skill_key else skill_key
                    desc = spell_data.get('desc', '无描述')
                    self.caller.msg(f"- {spell_data['name']} (|m{display_key}|n) (等级 {level}): {desc}")
                else:
                    # 只显示技能键名的最后一部分（例如 fire.fb 显示为 fb）
                    display_key = skill_key.split(".")[-1] if "." in skill_key else skill_key
                    self.caller.msg(f"- |m{display_key}|n (等级 {level})")
            except Exception as e:
                # 如果加载法术数据失败，显示基本技能信息
                display_key = skill_key.split(".")[-1] if "." in skill_key else skill_key
                self.caller.msg(f"- |m{display_key}|n (等级 {level})")