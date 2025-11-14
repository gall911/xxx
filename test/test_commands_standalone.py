#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化版命令测试脚本（不依赖Evennia环境）
"""

import os
import sys

# 添加项目路径
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_path)

def test_commands():
    """测试命令"""
    print("=== 测试命令结构 ===")
    
    try:
        # 测试学习命令
        from commands.skill_learn import CmdSkillLearn
        print(f"✓ 学习命令导入成功")
        
        # 测试施法命令
        from commands.cast import CmdCast
        print(f"✓ 施法命令导入成功")
        
        # 测试技能列表命令
        from commands.skills import CmdSkills
        print(f"✓ 技能列表命令导入成功")
        
        # 模拟命令实例化
        learn_cmd = object.__new__(CmdSkillLearn)
        cast_cmd = object.__new__(CmdCast)
        skills_cmd = object.__new__(CmdSkills)
        
        # 设置基本属性
        learn_cmd.key = "learn"
        cast_cmd.key = "cast"
        skills_cmd.key = "skills"
        
        print(f"✓ 学习命令实例创建成功: {learn_cmd.key}")
        print(f"✓ 施法命令实例创建成功: {cast_cmd.key}")
        print(f"✓ 技能列表命令实例创建成功: {skills_cmd.key}")
        
    except Exception as e:
        print(f"✗ 命令测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_command_functions():
    """测试命令功能"""
    print("\n=== 测试命令功能 ===")
    
    try:
        # 测试学习命令功能
        from commands.skill_learn import CmdSkillLearn
        
        # 创建模拟调用者
        class MockCaller:
            def __init__(self):
                self.db = type('obj', (object,), {'skills': {}})()
                
            def msg(self, text):
                print(f"  角色消息: {text}")
        
        # 测试学习命令执行
        mock_caller = MockCaller()
        learn_cmd = object.__new__(CmdSkillLearn)
        learn_cmd.caller = mock_caller
        learn_cmd.args = "fire.fireball"
        learn_cmd.func()
        
        print("✓ 学习命令功能测试成功")
        print(f"  当前技能: {mock_caller.db.skills}")
        
    except Exception as e:
        print(f"✗ 命令功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success1 = test_commands()
    success2 = test_command_functions()
    
    if success1 and success2:
        print("\n✓ 所有命令测试通过!")
    else:
        print("\n✗ 部分测试失败!")