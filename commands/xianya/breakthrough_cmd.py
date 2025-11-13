"""
突破境界命令
"""

from evennia import Command, default_cmds
from typeclasses.characters import Character

class CmdBreakthrough(default_cmds.MuxCommand):
    """
    突破境界

    用法:
      breakthrough
    """

    key = "breakthrough"
    aliases = ["突破", "bt"]
    locks = "cmd:all()"
    help_category = "修仙"

    def func(self):
        """实现突破境界功能"""

        # 检查是否是角色
        if not hasattr(self.caller, "db"):
            self.msg("只有角色可以使用此命令！")
            return

        # 调用角色的突破境界方法
        success = self.caller.breakthrough_realm()

        # 如果突破成功，记录日志
        if success:
            # TODO: 记录突破日志
            pass
