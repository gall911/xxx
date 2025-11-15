from evennia import Command
from evennia.utils import evtable
from evennia.utils import utils
import time

from typeclasses.magic import create_spell_from_path

class CmdCast(Command):
    key = "cast"
    aliases = ["cast"]
    locks = "cmd:all()"
    help_category = "Magic"

    def parse_spell_path(self, caller, token):
        """
        token could be:
         - 'fire>fb'
         - 'fb' (then look up in caller.db.skills for matching id)
        Returns full path like 'fire>fb' or None
        """
        token = token.strip()
        if ">" in token:
            return token
        # search caller skills for any entry ending with >token or equal token
        if hasattr(caller.db, 'skills'):
            for entry in caller.db.skills.keys():
                if entry.endswith(">" + token) or entry == token:
                    return entry
        # also allow token as full path if in global skills (factory will return None if not)
        return token

    def func(self):
        if not self.args:
            self.caller.msg("用法：cast <skill> <target>")
            return
        parts = self.args.split(None, 1)
        spell_token = parts[0]
        target_name = parts[1] if len(parts) > 1 else None
        if not target_name:
            self.caller.msg("指定目标： cast <skill> <target>")
            return
        # resolve spell path
        skill_path = self.parse_spell_path(self.caller, spell_token)
        if not skill_path:
            self.caller.msg("你不会这个技能。")
            return
        # check cooldown
        cds = getattr(self.caller.db, "cooldowns", {}) or {}
        cd_end = cds.get(skill_path, 0)
        now = time.time()
        if now < cd_end:
            left = int(cd_end - now)
            self.caller.msg(f"技能冷却中，还剩 {left} 秒。")
            return
        # find target
        target = self.caller.search(target_name)
        if not target:
            return
        # create spell instance
        spell = create_spell_from_path(skill_path)
        if not spell:
            self.caller.msg("未找到此技能的数据。")
            return
        # optional: check whether caster actually learned it
        if hasattr(self.caller.db, 'skills'):
            learned = False
            for entry in self.caller.db.skills.keys():
                if entry.endswith(">" + spell.id) or entry == skill_path:
                    learned = True
                    break
            if not learned:
                self.caller.msg("你还没学会这个技能。")
                return
        # optional: set a "casting lock" so player can't spam another cast
        if getattr(self.caller.ndb, "casting", None):
            self.caller.msg("你正在吟唱其它法术。")
            return
        # start casting
        spell.start_casting(self.caller, target)
        # immediate feedback (第一条通常由 stage 发出，如果没有 stages 则 start_casting 会 finish)
        self.caller.msg(f"你开始施放 {spell.key} 对 {target.key}。")