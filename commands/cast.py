from evennia import Command
from typeclasses.spells.loader import load_spell_data
from typeclasses.spells.spell_base import Spell
from typeclasses.combat.engine import check_cooldown
from evennia.utils import utils
import time
from typeclasses.spells.loader import load_spell_data, MAGIC_INDEX
class CmdCast(Command):
    """
    施放技能命令
    用法:
      cast 技能名 [目标]
    """
    key = "cast"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("施放什么技能？")
            return

        args = self.args.strip().split()
        spell_key = args[0].lower()

        # 后缀匹配技能
        matched_key = None
        if hasattr(self.caller.db, "skills"):
            for learned_key in self.caller.db.skills.keys():
                if learned_key.endswith("." + spell_key) or learned_key == spell_key:
                    matched_key = learned_key
                    break
        if matched_key:
            spell_key = matched_key
        else:
            self.caller.msg("你没有学会这个技能。")
            return

        # 冷却检查
        if check_cooldown(self.caller, spell_key):
            self.caller.msg("技能还在冷却中。")
            return

        data = load_spell_data(spell_key)
        if not data:
            self.caller.msg("未找到技能数据。")
            return

        # 获取目标
        target = None
        if len(args) > 1:
            target_name = args[1]
            for obj in self.caller.location.contents:
                if hasattr(obj, "key") and obj.key.lower() == target_name.lower():
                    target = obj
                    break
        if not target:
            self.caller.msg("你没有指定目标。")
            return

        # 启动法术
        spell = Spell(self.caller, spell_key, data, target)
        spell.start()