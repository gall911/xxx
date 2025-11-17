from evennia import Command
from typeclasses.spells.loader import load_spell_data, MAGIC_INDEX
class CmdSkills(Command):
    """
    查看已学技能列表命令
    """
    key = "skills"
    
    def func(self):
        """执行命令"""
        # 确保skills存在且是字典类型
        if not hasattr(self.caller.db, 'skills'):
            self.caller.msg("|m你还没有学会任何技能。|n")
            return
            
        # 获取skills字典，处理可能的序列化对象
        skills_dict = self.caller.db.skills
        if not skills_dict:
            self.caller.msg("|m你还没有学会任何技能。|n")
            return
            
        # 确保skills是字典类型（处理序列化对象）
        if not isinstance(skills_dict, dict):
            # 尝试转换为字典
            try:
                skills_dict = dict(skills_dict)
            except:
                self.caller.msg("|m技能数据格式错误。|n")
                return
        
        # 检查是否有技能
        if not skills_dict:
            self.caller.msg("|m你还没有学会任何技能。|n")
            return
            
        self.caller.msg("|m你已学会的技能：|n")
        for skill_key, skill_data in skills_dict.items():
            # 确保skill_data是字典类型
            if not isinstance(skill_data, dict):
                try:
                    skill_data = dict(skill_data)
                except:
                    skill_data = {"level": 1}
            
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