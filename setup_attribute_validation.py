#!/usr/bin/env python3
"""
角色属性验证规则设置脚本

这个脚本为角色属性配置添加验证规则。
"""

import sys
import os

# 添加config_system到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_system import get_config_loader

def setup_attribute_validation():
    """设置角色属性验证规则"""
    # 获取配置加载器
    loader = get_config_loader(enable_validation=True)

    print("设置角色属性验证规则...")

    # 验证基础属性定义
    attributes_path = "basic/attributes.attributes"

    # 验证属性名称
    for attr_name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
        loader.add_validation_rule(
            attributes_path, 
            f"{attr_name}.name", 
            "type", 
            expected_type="str",
            required=True
        )

        loader.add_validation_rule(
            attributes_path, 
            f"{attr_name}.description", 
            "type", 
            expected_type="str",
            required=True
        )

        loader.add_validation_rule(
            attributes_path, 
            f"{attr_name}.min_value", 
            "type", 
            expected_type="int",
            required=True
        )

        loader.add_validation_rule(
            attributes_path, 
            f"{attr_name}.max_value", 
            "type", 
            expected_type="int",
            required=True
        )

        loader.add_validation_rule(
            attributes_path, 
            f"{attr_name}.default_value", 
            "type", 
            expected_type="int",
            required=True
        )

        loader.add_validation_rule(
            attributes_path, 
            f"{attr_name}.growth_rate", 
            "type", 
            expected_type="float",
            required=True
        )

    # 验证公式定义
    formulas_path = "basic/attributes.formulas"

    for formula_name in ["health", "mana", "physical_attack", "magical_attack", 
                         "physical_defense", "magical_defense", "hit_rate", 
                         "dodge_rate", "critical_rate", "critical_damage"]:

        loader.add_validation_rule(
            formulas_path, 
            f"{formula_name}.base", 
            "type", 
            required=True
        )

        loader.add_validation_rule(
            formulas_path, 
            f"{formula_name}.formula", 
            "type", 
            expected_type="str",
            required=True
        )

    # 验证属性点分配系统
    attr_points_path = "basic/attributes.attribute_points"

    loader.add_validation_rule(
        attr_points_path, 
        "initial_points", 
        "type", 
        expected_type="int",
        required=True
    )

    loader.add_validation_rule(
        attr_points_path, 
        "points_per_level", 
        "type", 
        expected_type="int",
        required=True
    )

    # 验证种族属性修正
    race_mods_path = "basic/attributes.race_modifiers"

    for race_name in ["human", "elf", "dwarf", "orc", "halfling", "gnome"]:
        loader.add_validation_rule(
            race_mods_path, 
            f"{race_name}.name", 
            "type", 
            expected_type="str",
            required=True
        )

        loader.add_validation_rule(
            race_mods_path, 
            f"{race_name}.description", 
            "type", 
            expected_type="str",
            required=True
        )

        loader.add_validation_rule(
            race_mods_path, 
            f"{race_name}.modifiers", 
            "type", 
            expected_type="dict",
            required=True
        )

    # 验证职业属性修正
    class_mods_path = "basic/attributes.class_modifiers"

    for class_name in ["warrior", "mage", "ranger", "cleric", "rogue", "paladin"]:
        loader.add_validation_rule(
            class_mods_path, 
            f"{class_name}.name", 
            "type", 
            expected_type="str",
            required=True
        )

        loader.add_validation_rule(
            class_mods_path, 
            f"{class_name}.description", 
            "type", 
            expected_type="str",
            required=True
        )

        loader.add_validation_rule(
            class_mods_path, 
            f"{class_name}.primary_attribute", 
            "type", 
            expected_type="str",
            required=True
        )

        loader.add_validation_rule(
            class_mods_path, 
            f"{class_name}.secondary_attribute", 
            "type", 
            expected_type="str",
            required=True
        )

        loader.add_validation_rule(
            class_mods_path, 
            f"{class_name}.modifiers", 
            "type", 
            expected_type="dict",
            required=True
        )

    print("角色属性验证规则设置完成!")

    # 验证配置
    print("\n验证角色属性配置...")
    errors = loader.validate_config("basic/attributes")

    if errors:
        print("发现验证错误:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("角色属性配置验证通过!")

if __name__ == "__main__":
    setup_attribute_validation()
