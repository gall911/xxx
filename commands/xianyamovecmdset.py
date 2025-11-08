"""
仙侠风格移动命令集

包含使用仙侠风格描述的英文方向移动命令
"""

from evennia import CmdSet
from .xianyamovement import CmdNorth, CmdSouth, CmdEast, CmdWest

class XianyaMoveCmdSet(CmdSet):
    """
    仙侠风格移动命令集
    """
    
    key = "xianyamovecmdset"
    
    def at_cmdset_creation(self):
        """添加命令到命令集"""
        self.add(CmdNorth())
        self.add(CmdSouth())
        self.add(CmdEast())
        self.add(CmdWest())
