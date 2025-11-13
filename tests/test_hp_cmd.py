import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 创建模拟角色对象
class MockCharacter:
    def __init__(self):
        self.db = MockDB()

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

# 创建模拟Command类
class MockCommand:
    def __init__(self):
        self.caller = None
        self.key = "hp"
        self.locks = "cmd:all()"
        self.help_category = "通用"

    def msg(self, text):
        print(text)

# 直接导入hp命令的func方法
def test_hp_cmd():
    """测试hp命令"""
    print("创建测试角色...")

    # 创建一个模拟角色
    test_char = MockCharacter()

    # 创建hp命令实例
    hp_cmd = MockCommand()
    hp_cmd.caller = test_char

    # 获取hp命令的func方法
    from commands.hp_cmd import CmdHp

    # 将func方法绑定到hp_cmd实例
    hp_func = CmdHp.func.__get__(hp_cmd, MockCommand)

    print("执行hp命令...")
    # 执行命令
    hp_func()

    print("\n测试完成！")

if __name__ == "__main__":
    try:
        test_hp_cmd()
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
