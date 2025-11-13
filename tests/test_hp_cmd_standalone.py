# 模拟Evennia类
class Command:
    pass

class ANSIString(str):
    pass

# 模拟主题颜色
HP_BAR = "|r"
MP_BAR = "|b"
HP_SEPARATOR = "|y"
HP_LABEL = "|w"
HP_VALUE = "|n"
HP_GOLD = "|Y"
HP_SILVER = "|y"
HP_PERCENT_LOW = "|r"
HP_PERCENT_MID = "|y"
HP_PERCENT_HIGH = "|g"

def make_bar(value, max_value, length=10, color_full="|g█|n", color_empty="|K░|n"):
    """生成带颜色的等长进度条"""
    filled = int(length * value / max_value) if max_value else 0
    empty = length - filled
    return ANSIString(f"{color_full * filled}{color_empty * empty}")

class CmdHp(Command):
    """
    查看角色生命状态

    用法:
      hp

    显示你的角色当前生命状态，包括气血、真元等状态。
    """

    key = "hp"
    locks = "cmd:all()"
    help_category = "通用"

    def func(self):
        """执行命令"""
        caller = self.caller

        # 获取角色属性，使用getattr避免None值错误
        hp = getattr(caller.db, 'hp', 100)
        max_hp = getattr(caller.db, 'max_hp', 100)
        mp = getattr(caller.db, 'mana', 100)
        max_mp = getattr(caller.db, 'max_mana', 100)
        magic_power = getattr(caller.db, 'magic_power', 5)

        # 修仙相关属性
        cultivation = getattr(caller.db, 'cultivation', "凡人")
        cultivation_level = getattr(caller.db, 'cultivation_level', 0)
        spirit_power = getattr(caller.db, 'spirit_power', 10)

        # 基础属性
        constitution = getattr(caller.db, 'constitution', 10)
        strength = getattr(caller.db, 'strength', 10)
        dexterity = getattr(caller.db, 'dexterity', 10)
        intelligence = getattr(caller.db, 'intelligence', 10)

        # 金钱和经验
        gold = getattr(caller.db, 'gold', 0)
        silver = getattr(caller.db, 'silver', 0)
        exp = getattr(caller.db, 'exp', 0)
        level = getattr(caller.db, 'level', 1)
        exp_needed = getattr(caller.db, 'exp_needed', 100)

        # 确保所有值都不是None
        hp = 0 if hp is None else hp
        max_hp = 1 if max_hp is None or max_hp == 0 else max_hp
        mp = 0 if mp is None else mp
        max_mp = 1 if max_mp is None or max_mp == 0 else max_mp
        magic_power = 0 if magic_power is None else magic_power
        cultivation = "未知" if cultivation is None else cultivation
        cultivation_level = 0 if cultivation_level is None else cultivation_level
        spirit_power = 0 if spirit_power is None else spirit_power
        constitution = 0 if constitution is None else constitution
        strength = 0 if strength is None else strength
        dexterity = 0 if dexterity is None else dexterity
        intelligence = 0 if intelligence is None else intelligence
        gold = 0 if gold is None else gold
        silver = 0 if silver is None else silver
        exp = 0 if exp is None else exp
        level = 1 if level is None else level
        exp_needed = 1 if exp_needed is None or exp_needed == 0 else exp_needed

        # 计算百分比
        hp_percent = int(hp / max_hp * 100) if max_hp > 0 else 0
        mp_percent = int(mp / max_mp * 100) if max_mp > 0 else 0
        exp_percent = int(exp / exp_needed * 100) if exp_needed > 0 else 0

        # 根据百分比选择颜色
        hp_color = HP_PERCENT_LOW if hp_percent < 30 else (HP_PERCENT_MID if hp_percent < 70 else HP_PERCENT_HIGH)
        mp_color = HP_PERCENT_LOW if mp_percent < 30 else (HP_PERCENT_MID if mp_percent < 70 else HP_PERCENT_HIGH)
        exp_color = HP_PERCENT_LOW if exp_percent < 30 else (HP_PERCENT_MID if exp_percent < 70 else HP_PERCENT_HIGH)

        # 生成进度条
        hp_bar_color = "|r" if hp_percent < 30 else ("|y" if hp_percent < 70 else "|g")
        mp_bar_color = "|b" if mp_percent < 30 else ("|c" if mp_percent < 70 else "|B")
        exp_bar_color = "|r" if exp_percent < 30 else ("|y" if exp_percent < 70 else "|g")

        hp_bar = make_bar(hp, max_hp, 15, f"{hp_bar_color}█|n", "|K░|n")
        mp_bar = make_bar(mp, max_mp, 15, f"{mp_bar_color}█|n", "|K░|n")
        exp_bar = make_bar(exp, exp_needed, 15, f"{exp_bar_color}█|n", "|K░|n")

        # 构建显示文本
        text = f"""
{HP_LABEL}> 你目前的状态属性如下：{HP_VALUE}
{HP_SEPARATOR}≡{HP_VALUE}----------------------------------------------------------------{HP_SEPARATOR}≡{HP_VALUE}
{HP_LABEL}【 气 血 】{HP_VALUE} {HP_BAR}{hp:5}{HP_VALUE}/{max_hp:5} ({hp_color}{hp_percent:3}%{HP_VALUE}) {hp_bar}
{HP_LABEL}【 真 元 】{HP_VALUE} {MP_BAR}{mp:5}{HP_VALUE} / {max_mp:5} ({mp_color}{mp_percent:3}%{HP_VALUE}) {mp_bar}
{HP_LABEL}【 境 界 】{HP_VALUE} {cultivation} ({cultivation_level})    {HP_LABEL}【 灵 力 】{HP_VALUE} {spirit_power:5}
{HP_LABEL}【 体 质 】{HP_VALUE} {constitution:5}                    {HP_LABEL}【 力 量 】{HP_VALUE} {strength:5}
{HP_LABEL}【 敏 捷 】{HP_VALUE} {dexterity:5}                    {HP_LABEL}【 智 力 】{HP_VALUE} {intelligence:5}
{HP_LABEL}【 金 钱 】{HP_VALUE} {HP_GOLD}{gold}{HP_VALUE}金 {HP_SILVER}{silver}{HP_VALUE}银               {HP_LABEL}【 经 验 】{HP_VALUE} {exp:5}/{exp_needed:5} ({exp_color}{exp_percent:3}%{HP_VALUE}) {exp_bar}
{HP_SEPARATOR}≡{HP_VALUE}----------------------------------------------------------------{HP_SEPARATOR}≡{HP_VALUE}"""

        self.msg(text)

def test_hp_cmd():
    """测试hp命令"""
    print("创建测试角色...")

    # 创建模拟角色
    class MockDB:
        def __init__(self):
            self.hp = 80
            self.max_hp = 100
            self.mana = 60
            self.max_mana = 120
            self.magic_power = 15
            self.cultivation = "筑基"
            self.cultivation_level = 3
            self.spirit_power = 25
            self.constitution = 12
            self.strength = 15
            self.dexterity = 18
            self.intelligence = 14
            self.gold = 50
            self.silver = 120
            self.exp = 350
            self.level = 5
            self.exp_needed = 500

    class MockCharacter:
        def __init__(self):
            self.db = MockDB()

    class MockCommand:
        def __init__(self):
            self.caller = None
            self.key = "hp"
            self.locks = "cmd:all()"
            self.help_category = "通用"

        def msg(self, text):
            print(text)

    # 创建一个模拟角色
    test_char = MockCharacter()

    # 创建hp命令实例
    hp_cmd = MockCommand()
    hp_cmd.caller = test_char

    # 将func方法绑定到hp_cmd实例
    hp_func = CmdHp.func.__get__(hp_cmd, MockCommand)

    print("执行hp命令...")
    # 执行命令
    hp_func()

    print("\n测试完成！")

if __name__ == "__main__":
    test_hp_cmd()
