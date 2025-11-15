#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
技能系统测试脚本
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_skill_system():
    """测试技能系统功能"""
    print("测试技能系统...")
    
    try:
        # 导入必要的模块
        from typeclasses.spells.loader import load_spell_data, get_spell_key_by_name
        from commands.skill_learn import CmdSkillLearn
        from commands.skills import CmdSkills
        from commands.cast import CmdCast
        
        # 测试技能加载
        print("\n1. 测试技能加载:")
        spell_data = load_spell_data('fire.fireball')
        print(f"✓ 火球术数据加载成功: {spell_data['name']}")
        
        # 测试通过名称查找技能键
        print("\n2. 测试通过名称查找技能键:")
        spell_key = get_spell_key_by_name('火球术')
        print(f"✓ 火球术的技能键: {spell_key}")
        
        # 模拟玩家对象
        class MockPlayer:
            def __init__(self):
                self.db = type('obj', (object,), {
                    'skills': {},
                    'target': None
                })()
            
            def msg(self, text):
                print(f"玩家消息: {text}")
        
        # 测试学习技能
        print("\n3. 测试学习技能:")
        player = MockPlayer()
        learn_cmd = object.__new__(CmdSkillLearn)
        learn_cmd.caller = player
        learn_cmd.args = "fire.fireball"
        
        # 重定向输出以捕获消息
        original_msg = player.msg
        messages = []
        def capture_msg(text):
            messages.append(text)
            print(f"玩家消息: {text}")
        player.msg = capture_msg
        
        learn_cmd.func()
        player.msg = original_msg
        
        print(f"✓ 玩家技能: {player.db.skills}")
        
        # 测试技能列表显示
        print("\n4. 测试技能列表显示:")
        skills_cmd = object.__new__(CmdSkills)
        skills_cmd.caller = player
        skills_cmd.func()
        
        # 检查技能是否正确学习
        if 'fire.fireball' in player.db.skills:
            print("✓ 技能学习功能正常")
        else:
            print("✗ 技能学习功能异常")
            
        print("\n所有测试完成!")
        return True
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_skill_system()
    sys.exit(0 if success else 1)