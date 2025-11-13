from evennia import CmdSet

class XianyaCmdSet(CmdSet):
    """
    修仙风格命令集
    """

    key = "XianyaCmdSet"
    priority = 1  # 设置优先级，确保能覆盖默认命令

    def at_cmdset_creation(self):
        """当命令集创建时调用"""
        try:
            from .score_cmd import CmdScore
            self.add(CmdScore)
            print("修仙风格命令集已成功添加")
        except Exception as e:
            print(f"添加修仙风格命令时出错: {e}")
