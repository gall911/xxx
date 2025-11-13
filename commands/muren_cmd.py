from evennia import Command, create_object
from utils.config_manager import game_config

class CmdMuren(Command):
    """
    创建木人桩

    用法:
      muren [类型]

    类型:
      basic - 基础木人桩（默认）
      advanced - 高级木人桩
      master - 大师级木人桩

    示例:
      muren - 创建一个基础木人桩
      muren advanced - 创建一个高级木人桩
      muren master - 创建一个大师级木人桩
    """

    key = "muren"
    locks = "cmd:all()"
    help_category = "建造"

    def func(self):
        """执行命令"""
        # 获取木人桩类型
        dummy_type = self.args.strip().lower() if self.args else "basic"

        # 检查木人桩类型是否有效
        config = game_config.get_config("npcs/training_dummies")
        if not config or "training_dummies" not in config or dummy_type not in config["training_dummies"]:
            self.msg(f"无效的木人桩类型: {dummy_type}")
            self.msg("可用类型: basic, advanced, master")
            return

        # 创建木人桩
        muren = create_object("typeclasses.muren.Muren", key=f"木人桩")
        muren.set_dummy_type(dummy_type)

        # 将木人桩放置在当前位置
        muren.location = self.caller.location

        # 获取木人桩配置信息
        dummy_config = config["training_dummies"][dummy_type]
        name = dummy_config.get("name", "木人桩")
        description = dummy_config.get("description", "一个坚实的木人桩，上面布满了练习留下的痕迹。")

        # 设置木人桩的属性
        muren.key = name
        muren.db.desc = description

        # 通知创建成功
        self.msg(f"成功创建了一个{name}！")
        self.caller.location.msg_contents(f"{self.caller.name}挥手间，一个{name}拔地而起。", exclude=self.caller)
