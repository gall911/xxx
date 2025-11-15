#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')

def setup_django():
    """设置Django环境"""
    try:
        import django
        django.setup()
        return True
    except Exception as e:
        print(f"Django设置失败: {e}")
        return False

class MockPlayer:
    """模拟玩家对象"""
    def __init__(self):
        class DB:
            def __init__(self):
                # 模拟玩家学会的技能
                self.skills = {
                    'fire.fireball': {'level': 1},
                    'ice.iceball': {'level': 1},
                    'fire.fb': {'level': 1}
                }
        self.db = DB()
    
    def msg(self, text):
        """模拟发送消息给玩家"""
        print(text)

def test_cmd_skills():
    """测试技能命令"""
    print("测试技能命令...")
    
    # 设置Django环境
    if not setup_django():
        print("无法设置Django环境，测试终止")
        return
    
    try:
        # 导入技能命令
        from commands.skills import CmdSkills
        
        # 创建命令实例
        cmd = CmdSkills()
        cmd.caller = MockPlayer()
        
        # 执行命令
        print("\n执行 skills 命令:")
        cmd.func()
        
        print("\n测试完成!")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_cmd_skills()