"""
仙侠命令集

包含仙侠风格的移动命令
"""

from evennia import CmdSet
from .xianyamovecmd import (
    CmdNorth, CmdSouth, CmdEast, CmdWest,
    CmdNortheast, CmdNorthwest, CmdSoutheast, CmdSouthwest,
    CmdUp, CmdDown, CmdIn, CmdOut
)

class XianyaCmdSet(CmdSet):
    """
    仙侠命令集
    """
    
    key = "xianyacmdset"
    
    def at_cmdset_creation(self):
        """添加命令到命令集"""
        self.add(CmdNorth())
        self.add(CmdSouth())
        self.add(CmdEast())
        self.add(CmdWest())
        self.add(CmdNortheast())
        self.add(CmdNorthwest())
        self.add(CmdSoutheast())
        self.add(CmdSouthwest())
        self.add(CmdUp())
        self.add(CmdDown())
        self.add(CmdIn())
        self.add(CmdOut())
