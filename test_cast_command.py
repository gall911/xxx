#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import django

# 添加项目路径
sys.path.insert(0, '/home/gg/xxx')

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')
django.setup()

# 模拟玩家对象
class MockObject:
    def __init__(self, key):
        self.key = key
        self.aliases = []
        self.db = MockDB()
        
class MockDB:
    def __init__(self):
        self.hp = 100
        self.target = None

# 模拟房间对象
class MockRoom:
    def __init__(self):
        self.contents = []

# 模拟玩家
class MockPlayer:
    def __init__(self):
        self.db = MockDB()
        self.db.skills = {
            "fire.fireball": {"level": 1},
            "ice.iceball": {"level": 1},
            "fire.fb": {"level": 1}
        }
        self.location = MockRoom()
        self.ndb = MockDB()
        
    def msg(self, text):
        print(f"玩家消息: {text}")

# 导入施法命令
from commands.cast import CmdCast

def test_cast_command():
    """测试施法命令"""
    print("测试施法命令...")
    
    # 创建模拟玩家和命令
    player = MockPlayer()
    cmd = CmdCast()
    cmd.caller = player
    
    # 创建测试目标
    target = MockObject("haha")
    player.location.contents.append(target)
    player.db.target = target
    
    # 测试完整技能名称
    print("\n=== 测试完整技能名称 ===")
    cmd.args = "fire.fireball haha"
    print(f"执行命令: cast {cmd.args}")
    cmd.func()
    
    # 测试缩写技能名称
    print("\n=== 测试缩写技能名称 ===")
    cmd.args = "iceball haha"
    print(f"执行命令: cast {cmd.args}")
    cmd.func()
    
    # 测试火墙术缩写
    print("\n=== 测试火墙术缩写 ===")
    cmd.args = "fb haha"
    print(f"执行命令: cast {cmd.args}")
    cmd.func()

if __name__ == "__main__":
    test_cast_command()