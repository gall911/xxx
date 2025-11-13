from evennia import Command

class CmdAdd(Command):
    """
    添加或修改角色属性

    用法:
      add <属性> <值>

    示例:
      add hp 100    - 设置气血为100
      add mp 80     - 设置真元为80
      add sp 20     - 设置灵力为20
      add gold 50   - 设置金钱为50
      add exp 200   - 设置经验为200
      add strength 15 - 设置力量为15

    可用属性列表:
      基础属性:
        hp, 气血 - 气血值
        max_hp, 最大气血 - 最大气血值
        mp, mana, 真元 - 真元值
        max_mp, max_mana, 最大真元 - 最大真元值
        sp, spirit_power, 灵力 - 灵力值

      基本能力:
        strength, 力量 - 力量值
        constitution, 体质 - 体质值
        dexterity, 敏捷 - 敏捷值
        intelligence, 智力 - 智力值

      修仙相关:
        cultivation, 修为 - 修为境界
        cultivation_level, 境界等级 - 境界等级

      金钱与经验:
        gold, 金 - 金钱
        silver, 银 - 银钱
        exp, 经验 - 经验值
        exp_needed, 升级所需经验 - 升级所需经验
    """

    key = "add"
    locks = "cmd:all()"
    help_category = "通用"

    # 属性映射表
    attr_map = {
        'hp': 'hp',
        '气血': 'hp',
        'mp': 'mana',
        '真元': 'mana',
        'mana': 'mana',
        'sp': 'spirit_power',
        '灵力': 'spirit_power',
        'spirit_power': 'spirit_power',
        'gold': 'gold',
        '金': 'gold',
        'silver': 'silver',
        '银': 'silver',
        'exp': 'exp',
        '经验': 'exp',
        'strength': 'strength',
        '力量': 'strength',
        'constitution': 'constitution',
        '体质': 'constitution',
        'dexterity': 'dexterity',
        '敏捷': 'dexterity',
        'intelligence': 'intelligence',
        '智力': 'intelligence',
        'max_hp': 'max_hp',
        '最大气血': 'max_hp',
        'max_mp': 'max_mana',
        '最大真元': 'max_mana',
        'max_mana': 'max_mana',
        'cultivation': 'cultivation',
        '修为': 'cultivation',
        'cultivation_level': 'cultivation_level',
        '境界等级': 'cultivation_level',
    }

    def func(self):
        """执行命令"""
        if not self.args:
            self.msg("用法: add <属性> <值>")
            return

        args = self.args.split()
        if len(args) < 2:
            self.msg("用法: add <属性> <值>")
            return

        attr_name = args[0].lower()
        value_str = " ".join(args[1:])  # 支持带空格的值，比如境界名称

        # 查找属性映射
        if attr_name not in self.attr_map:
            self.msg(f"未知属性: {attr_name}")
            return

        db_attr = self.attr_map[attr_name]

        # 尝试转换值
        try:
            # 对于修为境界，保持为字符串
            if db_attr == 'cultivation':
                value = value_str
            else:
                # 尝试转换为整数
                value = int(value_str)
        except ValueError:
            self.msg(f"无效的值: {value_str}")
            return

        # 设置属性值
        setattr(self.caller.db, db_attr, value)

        # 获取当前值并显示
        current_value = getattr(self.caller.db, db_attr, "未知")
        self.msg(f"已设置 {attr_name} 为: {current_value}")
