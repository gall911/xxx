"""
系统命令集

包含系统管理相关的命令
"""

from evennia import CmdSet
from .fixexitcmd import CmdFixExit
from .testexitcmd import CmdTestExit
from .testcolorcmd import CmdTestColor
from .themecmd import CmdTheme
from .createroomcmd import CmdDig
from .quickdigcmd import CmdQuickDig
from .reloadcmd import CmdReloadCmds

class SysCmdSet(CmdSet):
    """
    系统管理命令集
    """
    
    key = "syscmdset"
    
    def at_cmdset_creation(self):
        """添加命令到命令集"""
        self.add(CmdFixExit())
        self.add(CmdTestExit())
        self.add(CmdTestColor())
        self.add(CmdTheme())
        self.add(CmdDig())
        self.add(CmdQuickDig())
        self.add(CmdReloadCmds())
