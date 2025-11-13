from evennia import Command

class CmdScore(Command):
    """
    查看角色属性信息

    用法:
      score
      sc

    显示你的角色当前状态，包括等级、经验、生命值、法力值等属性。
    """

    key = "score"
    aliases = ["sc", "属性", "状态"]
    locks = "cmd:all()"
    help_category = "通用"

    def func(self):
        """执行命令"""
        caller = self.caller

        # 使用角色类中的方法获取状态信息
        if hasattr(caller, 'get_xianya_status'):
            status = caller.get_xianya_status()
            self.msg(status)
        else:
            # 如果方法不存在，显示基本状态
            self.msg(f"|c【{caller.key}的状态】|n")
            self.msg(f"|w等级:|n 1")
            self.msg(f"|w气血:|n |r100|n/|r100|n")
            self.msg(f"|w真元:|n |b100|n/|b100|n")
