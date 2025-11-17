from evennia import Command
from typeclasses.spells.loader import load_spell_data, MAGIC_INDEX

class CmdSkillLearn(Command):
    """
    学习技能命令
    """
    key = "learn"
    locks = "cmd:all()"
    
    def func(self):
        """执行命令"""
        if not self.args:
            self.caller.msg("学习什么技能？")
            return
            
        spell_name_or_key = self.args.strip()
        
        # 查找技能键名
        spell_key = None
        
        # 首先尝试直接匹配技能键名
        if spell_name_or_key in MAGIC_INDEX:
            spell_key = spell_name_or_key
        else:
            # 尝试匹配技能键名的一部分（例如，对于"fire.fb"，允许用户输入"fb"）
            for key in MAGIC_INDEX.keys():
                if key.endswith('.' + spell_name_or_key) or key == spell_name_or_key:
                    spell_key = key
                    break
                        
        if not spell_key:
            self.caller.msg("找不到这个技能。")
            return
            
        # 检查是否已经学会了这个技能
        if hasattr(self.caller.db, 'skills') and self.caller.db.skills is not None and spell_key in self.caller.db.skills:
            self.caller.msg("你已经学会了这个技能。")
            return
            
        # 初始化技能字典（如果不存在或类型不正确）
        if not hasattr(self.caller.db, 'skills') or self.caller.db.skills is None or not isinstance(self.caller.db.skills, dict):
            self.caller.db.skills = {}
            
        # 获取技能数据以显示技能名称
        spell_data = load_spell_data(spell_key)
        
        # 添加技能到法术书
        self.caller.db.skills[spell_key] = {
            "level": 1,
            "proficiency": 0
        }
        
        if spell_data:
            self.caller.msg(f"你学会了{spell_data['name']}！")
        else:
            self.caller.msg(f"你学会了{spell_key}！")
        
        # 同时添加到spellbook中以兼容新的施法系统
        if not hasattr(self.caller.db, 'spellbook') or self.caller.db.spellbook is None:
            self.caller.db.spellbook = []
            
        # 将技能键转换为新的格式（group>id）
        if '.' in spell_key:
            parts = spell_key.split('.')
            new_format = f"{parts[0]}>{parts[1]}"
            if new_format not in self.caller.db.spellbook:
                self.caller.db.spellbook.append(new_format)
                self.caller.msg(f"技能已添加到你的法术书中（{new_format}）。")