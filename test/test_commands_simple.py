#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化版命令测试脚本
"""

import os
import sys

# 添加项目路径
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_path)

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')

def test_commands():
    """测试命令"""
    print("=== 测试命令 ===")
    
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
        
        # 创建命令实例
        learn_cmd = CmdSkillLearn()
        cast_cmd = CmdCast()
        skills_cmd = CmdSkills()
        
        print(f"✓ 学习命令实例创建成功: {learn_cmd.key}")
        print(f"✓ 施法命令实例创建成功: {cast_cmd.key}")
        print(f"✓ 技能列表命令实例创建成功: {skills_cmd.key}")
        
    except Exception as e:
        print(f"✗ 命令测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    test_commands()