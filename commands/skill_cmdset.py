from evennia import CmdSet
from .cast import CmdCast
from .hit import CmdHit
from .skill_learn import CmdSkillLearn
from .skills import CmdSkills

class SkillCmdSet(CmdSet):
    """技能系统命令集"""
    key = "skill_cmdset"

    def at_cmdset_creation(self):
        # 添加基本技能命令
        self.add(CmdCast)
        self.add(CmdHit)
        self.add(CmdSkillLearn)
        self.add(CmdSkills)
        # 不添加CmdMagicCast，因为与CmdCast冲突