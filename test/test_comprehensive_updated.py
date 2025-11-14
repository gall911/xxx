#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
技能系统综合测试脚本（更新版）
此脚本用于验证技能系统的各个组件是否正常工作
"""

import os
import sys
import json

# 添加项目路径
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_path)

def test_json_loading():
    """测试JSON文件加载"""
    print("=== 测试JSON文件加载 ===")
    
    # 测试技能索引文件
    try:
        index_file = os.path.join(project_path, "world", "magic", "magic_index.json")
        with open(index_file, "r", encoding="utf-8") as f:
            index_data = json.load(f)
        print(f"✓ 技能索引文件加载成功，包含 {len(index_data)} 个技能")
    except Exception as e:
        print(f"✗ 技能索引文件加载失败: {e}")
        return False
    
    # 测试火球术配置文件
    try:
        fireball_file = os.path.join(project_path, "world", "magic", "fire", "fireball.json")
        with open(fireball_file, "r", encoding="utf-8") as f:
            fireball_data = json.load(f)
        print(f"✓ 火球术配置文件加载成功: {fireball_data['name']}")
    except Exception as e:
        print(f"✗ 火球术配置文件加载失败: {e}")
        return False
    
    return True

def test_spell_loader():
    """测试技能加载器"""
    print("\n=== 测试技能加载器 ===")
    
    try:
        from typeclasses.spells.loader import load_spell_data, MAGIC_INDEX
        
        # 检查索引
        print(f"✓ 技能索引加载成功，包含 {len(MAGIC_INDEX)} 个技能")
        
        # 测试加载火球术
        fireball_spell = load_spell_data("fire.fireball")
        if fireball_spell:
            print(f"✓ 火球术数据加载成功: {fireball_spell['name']}")
        else:
            print("✗ 无法加载火球术数据")
            return False
            
    except Exception as e:
        print(f"✗ 技能加载器测试失败: {e}")
        return False
    
    return True

def test_damage_calculation():
    """测试伤害计算"""
    print("\n=== 测试伤害计算 ===")
    
    try:
        from typeclasses.spells.loader import load_spell_data
        
        # 加载火球术数据
        data = load_spell_data("fire.fireball")
        if not data:
            print("✗ 无法加载火球术数据")
            return False
            
        # 模拟不同等级的伤害计算
        base_dmg = data["damage"]["base"]
        per_level = data["damage"]["per_level"]
        
        print(f"火球术基础伤害: {base_dmg}")
        print(f"每级增量: {per_level}")
        
        # 计算1级伤害
        level_1_dmg = base_dmg + per_level * (1 - 1)
        print(f"1级火球术伤害: {level_1_dmg}")
        
        # 计算3级伤害
        level_3_dmg = base_dmg + per_level * (3 - 1)
        print(f"3级火球术伤害: {level_3_dmg}")
        
        # 验证计算结果
        if level_1_dmg == 50 and level_3_dmg == 70:
            print("✓ 伤害计算正确")
        else:
            print("✗ 伤害计算错误")
            return False
            
    except Exception as e:
        print(f"✗ 伤害计算测试失败: {e}")
        return False
    
    return True

def test_spell_class():
    """测试技能基类"""
    print("\n=== 测试技能基类 ===")
    
    try:
        from typeclasses.spells.spell_base import Spell
        
        # 创建模拟的数据和施法者
        class MockCaster:
            def __init__(self):
                self.db = type('obj', (object,), {})()
                
        mock_caster = MockCaster()
        mock_data = {"name": "测试技能", "type": "damage"}
        
        # 创建技能对象
        spell = Spell(mock_caster, mock_data)
        
        if spell.caster == mock_caster and spell.data == mock_data:
            print("✓ 技能基类工作正常")
        else:
            print("✗ 技能基类工作异常")
            return False
            
    except Exception as e:
        print(f"✗ 技能基类测试失败: {e}")
        return False
    
    return True

def test_command_structure():
    """测试命令结构"""
    print("\n=== 测试命令结构 ===")
    
    try:
        # 测试学习命令
        from commands.skill_learn import CmdSkillLearn
        learn_cmd = CmdSkillLearn()
        print(f"✓ 学习命令加载成功: {learn_cmd.key}")
        
        # 测试施法命令
        from commands.cast import CmdCast
        cast_cmd = CmdCast()
        print(f"✓ 施法命令加载成功: {cast_cmd.key}")
        
        # 测试技能列表命令
        from commands.skills import CmdSkills
        skills_cmd = CmdSkills()
        print(f"✓ 技能列表命令加载成功: {skills_cmd.key}")
        
    except Exception as e:
        print(f"✗ 命令结构测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def run_comprehensive_test():
    """运行综合测试"""
    print("开始技能系统综合测试...\n")
    
    tests = [
        test_json_loading,
        test_spell_loader,
        test_damage_calculation,
        test_spell_class,
        test_command_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
        else:
            print(f"测试 {test_func.__name__} 失败!")
    
    print(f"\n=== 测试结果 ===")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("✓ 所有测试通过！技能系统工作正常。")
        print("\n接下来可以在游戏中进行实际测试:")
        print("1. 学习技能: learn fire.fireball")
        print("2. 创建目标: create npc 测试目标")
        print("3. 攻击目标: hit 测试目标")
        print("4. 施放技能: cast fire.fireball")
        return True
    else:
        print("✗ 部分测试失败，请检查上述错误。")
        return False

if __name__ == "__main__":
    run_comprehensive_test()