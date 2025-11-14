#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
技能系统完整性测试脚本
"""

import os
import sys

def test_skill_system():
    """
    测试技能系统的完整性
    """
    print("=== 技能系统完整性测试 ===")
    
    # 1. 检查必要的目录和文件是否存在
    required_files = [
        "world/magic/magic_index.json",
        "world/magic/fire/fireball.json",
        "typeclasses/spells/spell_base.py",
        "typeclasses/spells/loader.py",
        "commands/cast.py",
        "commands/skill_learn.py",
        "commands/skills.py",
        "test/test_simple_fireball.py",
        "test/test_fireball_in_game.py"
    ]
    
    print("1. 检查必要文件...")
    missing_files = []
    for file_path in required_files:
        full_path = os.path.join("/home/gg/xxx", file_path)
        if not os.path.exists(full_path):
            missing_files.append(file_path)
            print(f"   缺失文件: {file_path}")
        else:
            print(f"   ✓ {file_path}")
    
    if missing_files:
        print(f"   发现 {len(missing_files)} 个缺失文件")
        return False
    else:
        print("   所有文件都存在")
    
    # 2. 检查技能索引文件格式
    print("\n2. 检查技能索引文件...")
    try:
        import json
        with open("/home/gg/xxx/world/magic/magic_index.json", "r", encoding="utf-8") as f:
            index_data = json.load(f)
        print("   ✓ 技能索引文件格式正确")
        print(f"   包含 {len(index_data)} 个技能")
    except Exception as e:
        print(f"   ✗ 技能索引文件格式错误: {e}")
        return False
    
    # 3. 检查火球术配置文件
    print("\n3. 检查火球术配置文件...")
    try:
        with open("/home/gg/xxx/world/magic/fire/fireball.json", "r", encoding="utf-8") as f:
            fireball_data = json.load(f)
        print("   ✓ 火球术配置文件格式正确")
        
        # 检查必要字段
        required_fields = ["name", "type", "damage", "mp_cost", "desc"]
        missing_fields = [field for field in required_fields if field not in fireball_data]
        if missing_fields:
            print(f"   ✗ 缺失必要字段: {missing_fields}")
            return False
        else:
            print("   ✓ 包含所有必要字段")
            
        # 检查伤害字段
        if "damage" in fireball_data:
            damage = fireball_data["damage"]
            if "base" not in damage or "per_level" not in damage:
                print("   ✗ 伤害字段不完整")
                return False
            else:
                print(f"   ✓ 伤害配置: 基础{damage['base']}, 每级{damage['per_level']}")
    except Exception as e:
        print(f"   ✗ 火球术配置文件格式错误: {e}")
        return False
    
    # 4. 测试技能加载器
    print("\n4. 测试技能加载器...")
    try:
        sys.path.append("/home/gg/xxx")
        from typeclasses.spells.loader import load_spell_data
        
        # 尝试加载火球术数据
        fireball_spell = load_spell_data("fire.fireball")
        if fireball_spell:
            print("   ✓ 技能加载器工作正常")
            print(f"   ✓ 成功加载火球术: {fireball_spell['name']}")
        else:
            print("   ✗ 无法加载火球术数据")
            return False
    except Exception as e:
        print(f"   ✗ 技能加载器测试失败: {e}")
        return False
    
    # 5. 测试简单测试脚本
    print("\n5. 测试简单测试脚本...")
    try:
        from test.test_simple_fireball import simple_test
        print("   ✓ 简单测试脚本可导入")
    except Exception as e:
        print(f"   ✗ 简单测试脚本导入失败: {e}")
        return False
    
    print("\n=== 测试完成 ===")
    print("✓ 技能系统完整性测试通过")
    print("\n现在可以在游戏中使用以下命令进行测试:")
    print("  @py import test.test_fireball_in_game; test.test_fireball_in_game.test_fireball()")
    print("或者手动测试:")
    print("  learn fire.fireball")
    print("  hit <目标>")
    print("  cast fire.fireball")
    
    return True

if __name__ == "__main__":
    test_skill_system()