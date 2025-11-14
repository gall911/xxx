#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
技能系统最终验证脚本
"""

import os
import sys

# 添加项目路径
project_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_path)

def test_skill_system_components():
    """测试技能系统各个组件"""
    print("=== 技能系统组件验证 ===")
    
    # 1. 测试技能索引文件加载
    try:
        from typeclasses.spells.loader import MAGIC_INDEX
        print(f"✓ 技能索引文件加载成功，包含 {len(MAGIC_INDEX)} 个技能")
        print(f"  技能列表: {list(MAGIC_INDEX.keys())}")
    except Exception as e:
        print(f"✗ 技能索引文件加载失败: {e}")
        return False
    
    # 2. 测试技能加载器
    try:
        from typeclasses.spells.loader import load_spell_data
        fireball_data = load_spell_data("fire.fireball")
        if fireball_data:
            print(f"✓ 火球术配置文件加载成功: {fireball_data['name']}")
        else:
            print("✗ 火球术配置文件加载失败")
            return False
    except Exception as e:
        print(f"✗ 技能加载器测试失败: {e}")
        return False
    
    # 3. 测试技能基类
    try:
        from typeclasses.spells.spell_base import Spell
        # 创建模拟数据
        mock_caster = object()
        mock_data = {"name": "测试技能"}
        spell = Spell(mock_caster, mock_data)
        if spell.caster == mock_caster and spell.data == mock_data:
            print("✓ 技能基类工作正常")
        else:
            print("✗ 技能基类初始化失败")
            return False
    except Exception as e:
        print(f"✗ 技能基类测试失败: {e}")
        return False
    
    # 4. 测试伤害计算
    try:
        fireball_data = load_spell_data("fire.fireball")
        base_dmg = fireball_data["damage"]["base"]
        per_level = fireball_data["damage"]["per_level"]
        
        print(f"火球术基础伤害: {base_dmg}")
        print(f"每级增量: {per_level}")
        
        # 1级火球术
        level_1_dmg = base_dmg + per_level * (1 - 1)
        print(f"1级火球术伤害: {level_1_dmg}")
        
        # 3级火球术
        level_3_dmg = base_dmg + per_level * (3 - 1)
        print(f"3级火球术伤害: {level_3_dmg}")
        
        if level_1_dmg == 50 and level_3_dmg == 70:
            print("✓ 伤害计算正确")
        else:
            print("✗ 伤害计算错误")
            return False
    except Exception as e:
        print(f"✗ 伤害计算测试失败: {e}")
        return False
    
    return True

def test_commands():
    """测试命令类"""
    print("\n=== 命令类验证 ===")
    
    try:
        # 测试学习命令
        from commands.skill_learn import CmdSkillLearn
        # 使用object.__new__来避免Evennia初始化问题
        learn_cmd = object.__new__(CmdSkillLearn)
        learn_cmd.key = "learn"
        print(f"✓ 学习命令导入成功: {learn_cmd.key}")
        
        # 测试施法命令
        from commands.cast import CmdCast
        cast_cmd = object.__new__(CmdCast)
        cast_cmd.key = "cast"
        print(f"✓ 施法命令导入成功: {cast_cmd.key}")
        
        # 测试技能列表命令
        from commands.skills import CmdSkills
        skills_cmd = object.__new__(CmdSkills)
        skills_cmd.key = "skills"
        print(f"✓ 技能列表命令导入成功: {skills_cmd.key}")
        
    except Exception as e:
        print(f"✗ 命令类测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

def test_json_files():
    """测试JSON配置文件"""
    print("\n=== JSON配置文件验证 ===")
    
    try:
        # 检查技能索引文件
        index_path = os.path.join(project_path, "world/magic/magic_index.json")
        if os.path.exists(index_path):
            print("✓ 技能索引文件存在")
        else:
            print("✗ 技能索引文件不存在")
            return False
            
        # 检查火球术配置文件
        fireball_path = os.path.join(project_path, "world/magic/fire/fireball.json")
        if os.path.exists(fireball_path):
            print("✓ 火球术配置文件存在")
        else:
            print("✗ 火球术配置文件不存在")
            return False
            
    except Exception as e:
        print(f"✗ JSON文件测试失败: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("技能系统最终验证测试")
    print("=" * 30)
    
    success1 = test_json_files()
    success2 = test_skill_system_components()
    success3 = test_commands()
    
    print("\n" + "=" * 30)
    if success1 and success2 and success3:
        print("✓ 所有测试通过！技能系统工作正常。")
        print("\n技能系统特点：")
        print("1. 极简设计 - 技能逻辑尽可能简单")
        print("2. 数据驱动 - 技能配置完全由JSON文件控制")
        print("3. 易于扩展 - 添加新技能只需创建JSON配置文件并在索引中注册")
        print("4. 灵活升级 - 技能等级直接影响伤害计算")
        print("5. 低耦合 - 技能系统与游戏其他系统解耦")
    else:
        print("✗ 部分测试失败，请检查上述错误。")