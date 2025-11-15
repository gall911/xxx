#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# 添加项目路径
sys.path.insert(0, '/home/gg/xxx')

# 导入必要的模块
from typeclasses.spells.loader import load_spell_data

# 模拟冷却检查函数
def mock_check_cooldown(caster, spell_key):
    """模拟冷却检查"""
    return False

# 模拟玩家数据库
class MockDB:
    def __init__(self):
        self.skills = {
            "fire.fireball": {"level": 1},
            "ice.iceball": {"level": 1},
            "fire.fb": {"level": 1}
        }
        self.target = None

# 模拟玩家对象
class MockPlayer:
    def __init__(self):
        self.db = MockDB()
        self.ndb = MockDB()
        
    def msg(self, text):
        print(f"玩家消息: {text}")

def simulate_cast_command(player, spell_input):
    """模拟施法命令"""
    print(f"\n执行命令: cast {spell_input}")
    
    # 解析技能键和目标
    args = spell_input.strip().split()
    spell_key = args[0].lower() if args else ""
    
    # 如果技能键不包含点号，尝试匹配已学会的技能
    if '.' not in spell_key:
        matched_key = None
        if hasattr(player.db, 'skills'):
            # 遍历已学会的技能，查找匹配的技能
            for learned_skill_key in player.db.skills.keys():
                # 检查技能键的后缀是否匹配（例如 fire.fb 匹配 fb）
                if learned_skill_key.endswith('.' + spell_key):
                    matched_key = learned_skill_key
                    break
                
                # 也检查完整键名是否匹配
                if learned_skill_key == spell_key:
                    matched_key = learned_skill_key
                    break
        
        if matched_key:
            spell_key = matched_key
        else:
            player.msg("你没有学会这个技能。")
            return
    else:
        # 判断是否已学会
        if not hasattr(player.db, 'skills') or spell_key not in player.db.skills:
            player.msg("你没有学会这个技能。")
            return
    
    # 加载技能数据
    data = load_spell_data(spell_key)
    if not data:
        player.msg("未找到此技能的数据。")
        return
        
    # 检查是否在冷却中
    if mock_check_cooldown(player, spell_key):
        player.msg("技能还在冷却中。")
        return
    
    # 获取技能信息
    spell_name = data.get('name', '未知技能')
    spell_desc = data.get('desc', '无描述')
    
    player.msg(f"成功施放 {spell_name} ({spell_key})")
    player.msg(f"技能描述: {spell_desc}")

def test_cast_scenarios():
    """测试各种施法场景"""
    print("=== 施法命令测试 ===")
    
    # 创建模拟玩家
    player = MockPlayer()
    
    # 测试场景
    scenarios = [
        "fire.fireball",      # 完整技能键
        "iceball haha",       # 缩写形式 + 目标
        "fb zombie",          # 火墙术缩写 + 目标
        "unknown"             # 未知技能
    ]
    
    for scenario in scenarios:
        simulate_cast_command(player, scenario)

if __name__ == "__main__":
    test_cast_scenarios()