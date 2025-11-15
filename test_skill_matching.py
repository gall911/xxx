#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# 添加项目路径
sys.path.insert(0, '/home/gg/xxx')

# 导入技能加载器
from typeclasses.spells.loader import load_spell_data

def match_spell_key(spell_key, learned_skills):
    """
    根据5.txt的思路实现技能匹配逻辑
    """
    # 如果技能键包含点号，直接检查是否已学会
    if '.' in spell_key:
        if spell_key in learned_skills:
            return spell_key
        else:
            return None
    
    # 如果技能键不包含点号，尝试匹配已学会的技能
    matched_key = None
    # 遍历已学会的技能，查找匹配的技能
    for learned_skill_key in learned_skills.keys():
        # 检查技能键的后缀是否匹配（例如 fire.fb 匹配 fb）
        if learned_skill_key.endswith('.' + spell_key):
            matched_key = learned_skill_key
            break
        
        # 也检查完整键名是否匹配
        if learned_skill_key == spell_key:
            matched_key = learned_skill_key
            break
    
    return matched_key

def test_spell_matching():
    """测试技能匹配逻辑"""
    print("测试技能匹配逻辑...")
    
    # 模拟玩家已学会的技能
    learned_skills = {
        "fire.fireball": {"level": 1},
        "ice.iceball": {"level": 1},
        "fire.fb": {"level": 1}
    }
    
    # 测试用例
    test_cases = [
        "fire.fireball",  # 完整键名
        "iceball",        # 缩写形式
        "fb",             # 火墙术缩写
        "unknown"         # 未知技能
    ]
    
    for spell_key in test_cases:
        print(f"\n测试技能键: '{spell_key}'")
        matched_key = match_spell_key(spell_key, learned_skills)
        if matched_key:
            print(f"  匹配成功: '{matched_key}'")
            # 加载技能数据
            data = load_spell_data(matched_key)
            if data:
                print(f"  技能名称: {data.get('name', '未知')}")
                print(f"  技能描述: {data.get('desc', '无描述')}")
            else:
                print(f"  无法加载技能数据")
        else:
            print(f"  匹配失败: 未找到对应的技能")

if __name__ == "__main__":
    test_spell_matching()