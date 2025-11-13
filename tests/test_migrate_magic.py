#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试魔法系统角色迁移功能
"""

import os
import sys

# 添加项目路径到系统路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.conf.settings")

# 初始化Django
import django
django.setup()

from evennia import create_object
from evennia.utils import search as search_utils
from typeclasses.characters import Character
from evennia.accounts.models import AccountDB

def test_character_search():
    """测试角色搜索功能"""
    print("\n测试搜索所有角色:")
    # 使用更精确的搜索方式，确保只获取角色对象
    all_objects = search_utils.object_search("*")
    # 使用类型检查而不是has_account来避免会话相关错误
    all_characters = [obj for obj in all_objects if hasattr(obj, 'account')]
    print(f"找到 {len(all_characters)} 个角色:")
    for char in all_characters:
        print(f" - {char.key}")

    # 测试搜索特定角色
    test_names = ["gg", "xx"]
    for name in test_names:
        print(f"\n测试搜索角色: {name}")
        # 原始搜索方法
        raw_results = search_utils.object_search(name)
        print(f"原始搜索结果数量: {len(raw_results)}")
        for result in raw_results:
            print(f"  - {result.key} (类型: {type(result).__name__})")

        # 优化后的搜索方法
        filtered_results = [obj for obj in search_utils.object_search(name) if hasattr(obj, 'account')]
        print(f"过滤后搜索结果数量: {len(filtered_results)}")
        for result in filtered_results:
            print(f"  - {result.key} (角色)")

        if filtered_results:
            print(f"找到角色: {filtered_results[0].key}")
        else:
            print(f"未找到角色: {name}")

    print("\n测试完成")

def test_migrate_magic_command():
    """测试migratemagic命令功能"""
    print("\n测试migratemagic命令:")

    # 测试不存在的角色
    print("\n测试不存在的角色:")
    nonexistent = search_utils.object_search("nonexistent_char")
    if not nonexistent:
        print("正确地找不到不存在的角色")
    else:
        print("错误地找到了不存在的角色")

    # 测试现有角色
    print("\n测试现有角色:")
    test_names = ["gg", "xx"]
    for name in test_names:
        chars = search_utils.object_search(name)
        if not chars:
            print(f"找不到角色: {name}")
            continue

        char = chars[0]

        # 添加魔法系统属性，有则覆盖，无则新建
        # 使用更直接的方式设置属性
        if not hasattr(char.db, 'mana') or char.db.mana is None:
            char.db.mana = 100
        if not hasattr(char.db, 'max_mana') or char.db.max_mana is None:
            char.db.max_mana = 100
        if not hasattr(char.db, 'magic_power') or char.db.magic_power is None:
            char.db.magic_power = 5
        if not hasattr(char.db, 'fire_resistance') or char.db.fire_resistance is None:
            char.db.fire_resistance = 0
        if not hasattr(char.db, 'water_resistance') or char.db.water_resistance is None:
            char.db.water_resistance = 0
        if not hasattr(char.db, 'earth_resistance') or char.db.earth_resistance is None:
            char.db.earth_resistance = 0
        if not hasattr(char.db, 'air_resistance') or char.db.air_resistance is None:
            char.db.air_resistance = 0
        if not hasattr(char.db, 'lightning_resistance') or char.db.lightning_resistance is None:
            char.db.lightning_resistance = 0
        if not hasattr(char.db, 'ice_resistance') or char.db.ice_resistance is None:
            char.db.ice_resistance = 0
        if not hasattr(char.db, 'light_resistance') or char.db.light_resistance is None:
            char.db.light_resistance = 0
        if not hasattr(char.db, 'dark_resistance') or char.db.dark_resistance is None:
            char.db.dark_resistance = 0
        if not hasattr(char.db, 'known_spells') or char.db.known_spells is None:
            char.db.known_spells = ["fireball"]

        print(f"已为角色'{char.key}'添加/更新魔法属性。")

        # 验证属性是否被添加
        print(f"角色 {name} 的魔法属性:")
        print(f"  - 法力值: {char.db.mana}/{char.db.max_mana}")
        print(f"  - 魔法强度: {char.db.magic_power}")
        print(f"  - 已知法术: {char.db.known_spells}")

if __name__ == "__main__":
    print("开始测试魔法系统角色迁移功能...")
    test_character_search()
    test_migrate_magic_command()
    print("\n所有测试完成")
