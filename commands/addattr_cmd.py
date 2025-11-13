from evennia import Command

class CmdAddAttr(Command):
    """
    添加或修改角色属性

    用法:
      addattr <属性名> <值>

    可修改的属性包括:
      hp - 气血值
      max_hp - 最大气血值
      mana/MP - 真元值
      max_mana/max_MP - 最大真元值
      sp/spirit_power - 灵力
      cultivation - 修为境界
      cultivation_level - 境界等级
      constitution - 体质
      strength - 力量
      dexterity - 敏捷
      intelligence - 智力
      gold - 金钱
      silver - 银钱
      exp - 经验值
      exp_needed - 升级所需经验

    示例:
      addattr hp 100
      addattr max_hp 150
      addattr mana 80
      addattr gold 50
    """

    key = "addattr"
    locks = "cmd:all()"
    help_category = "通用"

    # 属性映射表
    attr_map = {
        # 基础属性
        'hp': 'hp',
        '气血': 'hp',
        'max_hp': 'max_hp',
        '最大气血': 'max_hp',
        'mana': 'mana',
        'MP': 'mana',
        '真元': 'mana',
        'max_mana': 'max_mana',
        'max_MP': 'max_mana',
        '最大真元': 'max_mana',
        'sp': 'spirit_power',
        'spirit_power': 'spirit_power',
        '灵力': 'spirit_power',

        # 修仙属性
        'cultivation': 'cultivation',
        '修为': 'cultivation',
        'cultivation_level': 'cultivation_level',
        '境界等级': 'cultivation_level',

        # 基础属性
        'constitution': 'constitution',
        '体质': 'constitution',
        'strength': 'strength',
        '力量': 'strength',
        'dexterity': 'dexterity',
        '敏捷': 'dexterity',
        'intelligence': 'intelligence',
        '智力': 'intelligence',

        # 金钱和经验
        'gold': 'gold',
        '金': 'gold',
        '金钱': 'gold',
        'silver': 'silver',
        '银': 'silver',
        '银钱': 'silver',
        'exp': 'exp',
        '经验': 'exp',
        '经验值': 'exp',
        'exp_needed': 'exp_needed',
        '升级所需经验': 'exp_needed',
    }

    def func(self):
        """执行命令"""
        if not self.args:
            self.msg("用法: addattr <属性名> <值>")
            return

        args = self.args.split()
        if len(args) < 2:
            self.msg("用法: addattr <属性名> <值>")
            return

        attr_name = args[0].lower()
        value_str = args[1]

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
        self.msg(f"已设置 {attr_name}({db_attr}) 为: {current_value}")
