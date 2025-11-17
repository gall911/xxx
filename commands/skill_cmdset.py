from evennia import CmdSet
from .cast import CmdCast
from .hit import CmdHit
from .skill_learn import CmdSkillLearn
from .skills import CmdSkills
from .spellbook import CmdSpellbook

class SkillCmdSet(CmdSet):
    """技能系统命令集"""
    key = "SkillCmdSet"

    def at_cmdset_creation(self):
        """初始化命令集"""
        self.add(CmdSkillLearn())
        self.add(CmdSkills())
        self.add(CmdSpellbook())
        self.add(CmdCast())
        self.add(CmdHit())