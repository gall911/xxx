# 测试 score 命令
# 使用方法: 在游戏中运行 python test_score.py

import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from evennia import create_object
from typeclasses.characters import Character
from commands.score_cmd import CmdScore
from utils.config_manager import game_config

def test_score_command():
    """测试 score 命令的显示效果"""

    # 创建一个测试角色
    test_char = create_object(Character, key="测试角色")

    # 设置一些测试属性
    test_char.db.cultivation = "凡人"
    test_char.db.cultivation_level = 0
    test_char.db.level = 1
    test_char.db.exp = 50
    test_char.db.exp_needed = 100
    test_char.db.hp = 80
    test_char.db.max_hp = 100
    test_char.db.mana = 60
    test_char.db.max_mana = 100
    test_char.db.magic_power = 5
    test_char.db.spirit_power = 10
    test_char.db.strength = 10
    test_char.db.dexterity = 10  # 注意这里使用 dexterity 而不是 agility
    test_char.db.intelligence = 10
    test_char.db.constitution = 10
    test_char.db.gold = 10
    test_char.db.silver = 50
    test_char.db.known_spells = ["fireball"]

    # 创建 score 命令实例
    score_cmd = CmdScore()
    score_cmd.caller = test_char

    # 捕获输出
    class MockCaller:
        def __init__(self):
            self.msg_output = ""

        def msg(self, text):
            self.msg_output = text

    mock_caller = MockCaller()
    score_cmd.caller = mock_caller

    # 执行命令
    score_cmd.func()

    # 打印结果
    print("=== Score 命令输出 ===")
    print(mock_caller.msg_output)

    # 检查属性名称是否一致
    realms_config = game_config.get_config("basic/realms")
    attributes_config = game_config.get_config("basic/attributes")

    print("
=== 配置检查 ===")
    print(f"境界配置: {realms_config.get('realms', {}).get('凡人', {}).get('name', '未找到')}")
    print(f"属性配置:")
    for attr, config in attributes_config.get('attributes', {}).items():
        print(f"  {attr}: {config.get('name', '未找到')}")

if __name__ == "__main__":
    test_score_command()
