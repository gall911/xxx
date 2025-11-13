#!/usr/bin/env python3
"""
角色属性系统示例

这个示例展示了如何使用配置系统中的角色属性配置。
"""

import sys
import os
import math

# 添加config_system到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_system import get_config_loader

class Character:
    """角色类"""

    def __init__(self, name, level=1, race="human", character_class="warrior"):
        self.name = name
        self.level = level
        self.race = race
        self.character_class = character_class

        # 获取配置加载器
        self.config_loader = get_config_loader()

        # 加载属性配置
        self.attributes_config = self.config_loader.get_config("basic/attributes")

        # 初始化属性
        self.attributes = {}
        self.derived_attributes = {}

        # 初始化角色
        self._initialize_character()

    def _initialize_character(self):
        """初始化角色属性"""
        # 获取种族和职业修正
        race_mods = self.attributes_config["race_modifiers"][self.race]["modifiers"]
        class_mods = self.attributes_config["class_modifiers"][self.character_class]["modifiers"]

        # 初始化基础属性
        for attr_name, attr_data in self.attributes_config["attributes"].items():
            # 获取默认值
            value = attr_data["default_value"]

            # 应用种族修正
            if attr_name in race_mods:
                value = int(value * race_mods[attr_name])

            # 应用职业修正
            if attr_name in class_mods:
                value = int(value * class_mods[attr_name])

            # 确保在有效范围内
            value = max(attr_data["min_value"], min(attr_data["max_value"], value))

            self.attributes[attr_name] = value

        # 计算衍生属性
        self._calculate_derived_attributes()

    def _calculate_derived_attributes(self):
        """计算衍生属性"""
        for attr_name, formula_data in self.attributes_config["formulas"].items():
            # 获取基础值
            base_value = formula_data["base"]

            # 准备计算环境
            env = {
                "base": base_value,
                "level": self.level,
                "min": min,
                "max": max,
                "int": int,
                "float": float,
                "round": round,
                "math": math,
                # 添加所有属性
                **self.attributes
            }

            # 计算属性值
            try:
                value = eval(formula_data["formula"], {"__builtins__": {}}, env)
                self.derived_attributes[attr_name] = value
            except Exception as e:
                print(f"计算属性 {attr_name} 失败: {e}")
                self.derived_attributes[attr_name] = base_value

    def level_up(self):
        """升级角色"""
        self.level += 1

        # 获取主属性和副属性
        class_data = self.attributes_config["class_modifiers"][self.character_class]
        primary_attr = class_data["primary_attribute"]
        secondary_attr = class_data["secondary_attribute"]

        # 根据成长率增加属性
        for attr_name, attr_data in self.attributes_config["attributes"].items():
            growth_rate = attr_data["growth_rate"]

            # 主属性和副属性有额外加成
            if attr_name == primary_attr:
                growth_rate *= 1.5
            elif attr_name == secondary_attr:
                growth_rate *= 1.2

            # 增加属性值
            increase = int(growth_rate)
            if attr_name in [primary_attr, secondary_attr] and (growth_rate % 1) >= 0.5:
                increase += 1

            self.attributes[attr_name] = min(
                attr_data["max_value"], 
                self.attributes[attr_name] + increase
            )

        # 重新计算衍生属性
        self._calculate_derived_attributes()

        print(f"{self.name} 升级到 {self.level} 级!")

    def print_info(self):
        """打印角色信息"""
        print(f"\n===== {self.name} (Lv.{self.level} {self.race} {self.character_class}) =====")

        print("\n基础属性:")
        for attr_name, value in self.attributes.items():
            attr_data = self.attributes_config["attributes"][attr_name]
            print(f"  {attr_data['name']}({attr_name}): {value}")

        print("\n衍生属性:")
        for attr_name, value in self.derived_attributes.items():
            if attr_name in ["health", "mana"]:
                print(f"  {attr_name}: {int(value)}")
            elif attr_name in ["hit_rate", "dodge_rate", "critical_rate"]:
                print(f"  {attr_name}: {value:.2%}")
            else:
                print(f"  {attr_name}: {value:.2f}")

def main():
    """主函数"""
    print("=== 角色属性系统示例 ===")

    # 创建角色
    warrior = Character("勇者", level=5, race="human", character_class="warrior")
    warrior.print_info()

    # 升级角色
    warrior.level_up()
    warrior.print_info()

    # 创建不同种族和职业的角色
    elf_mage = Character("精灵法师", level=5, race="elf", character_class="mage")
    elf_mage.print_info()

    dwarf_warrior = Character("矮人战士", level=5, race="dwarf", character_class="warrior")
    dwarf_warrior.print_info()

    # 演示配置热更新
    print("\n现在您可以修改 configs/basic/attributes.yaml 文件，然后按回车键重新加载配置...")
    input()

    # 重新加载配置
    config_loader = get_config_loader()
    config_loader.reload_config("basic/attributes")

    # 重新计算角色属性
    print("\n重新加载配置后，重新计算角色属性:")
    warrior._initialize_character()
    warrior.print_info()

if __name__ == "__main__":
    main()
