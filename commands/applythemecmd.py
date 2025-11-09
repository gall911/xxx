"""
应用主题命令
"""

from evennia import Command
from utils.theme_hooks import apply_theme_to_all_objects

class CmdApplyTheme(Command):
    """
    应用主题到所有对象
    
    用法:
      applytheme
    """
    key = "applytheme"
    locks = "cmd:all()"

    def func(self):
        """执行命令"""
        caller = self.caller
        count = apply_theme_to_all_objects()
        caller.msg(f"已将当前主题应用到 {count} 个对象。")