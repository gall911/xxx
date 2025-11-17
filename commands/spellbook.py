from evennia import Command
from typeclasses.spells.loader import load_spell_data, MAGIC_INDEX

class CmdSpellbook(Command):
    """
    查看技能书命令
    """
    key = "spellbook"
    aliases = ["spells", "法术书"]
    locks = "cmd:all()"
    
    def func(self):
        """执行命令"""
        if not hasattr(self.caller.db, 'spellbook') or not self.caller.db.spellbook:
            self.caller.msg("你的技能书是空的。")
            return
            
        self.caller.msg("你的技能书包含以下技能：")
        for spell_entry in self.caller.db.spellbook:
            # 将新格式转换回旧格式以查找技能数据
            if '>' in spell_entry:
                group, id = spell_entry.split('>')
                spell_key = f"{group}.{id}"
            else:
                spell_key = spell_entry
                
            # 获取技能数据
            spell_data = load_spell_data(spell_key)
            if spell_data:
                level = 1
                if hasattr(self.caller.db, 'skills') and spell_key in self.caller.db.skills:
                    level = self.caller.db.skills[spell_key].get("level", 1)
                self.caller.msg(f"- {spell_data['name']} (等级 {level}): {spell_data['desc']}")
            else:
                self.caller.msg(f"- {spell_entry} (未知技能)")