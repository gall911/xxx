
# 初始化魔法属性的命令

from evennia import Command

class CmdInitMagic(Command):
    """
    为当前角色初始化魔法属性

    用法:
      initmagic
    """

    key = "initmagic"
    locks = "cmd:all()"
    help_category = "魔法"

    def func(self):
        """执行命令"""
        caller = self.caller

        # 检查是否已有魔法属性
        if hasattr(caller.db, 'mana'):
            caller.msg("你已经有魔法属性了。")
            return

        # 添加魔法属性
        caller.db.mana = 100
        caller.db.max_mana = 100
        caller.db.magic_power = 5
        caller.db.fire_resistance = 0
        caller.db.water_resistance = 0
        caller.db.earth_resistance = 0
        caller.db.air_resistance = 0
        caller.db.lightning_resistance = 0
        caller.db.ice_resistance = 0
        caller.db.light_resistance = 0
        caller.db.dark_resistance = 0

        # 添加已知法术
        caller.db.known_spells = ["fireball"]

        # 初始化法术冷却时间
        caller.spell_cooldowns = {}

        caller.msg("|g魔法属性已成功初始化！|n")
        caller.msg("你现在可以使用魔法命令了，试试输入 |wspells|n 查看你已学会的法术。")
