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

        # 使用角色类中的美化的状态显示方法
        if hasattr(caller, 'get_xianya_status'):
            text = caller.get_xianya_status()
        else:
            # 如果没有该方法，使用基本显示
            text = f"|c【{caller.key}的状态】|n\n无法获取详细信息，请联系管理员。"

        self.msg(text)
