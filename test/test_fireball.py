#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
火球术测试脚本

这个脚本测试火球术技能的功能，包括：
1. 学习火球术技能
2. 设置攻击目标
3. 施放火球术
4. 验证伤害效果

使用方法：
1. 在游戏中运行: @py import test_fireball; test_fireball.run_test()
"""

def run_test():
    """运行火球术测试"""
    # 获取当前角色
    me = __import__('evennia').search_script('me').get()
    
    # 初始化角色属性
    me.db.skills = {}
    me.db.hp = 100
    me.db.max_hp = 100
    me.db.mp = 100
    me.db.max_mp = 100
    
    me.msg("=== 火球术测试开始 ===")
    me.msg(f"角色初始状态 - HP: {me.db.hp}/{me.db.max_hp}, MP: {me.db.mp}/{me.db.max_mp}")
    
    # 1. 学习火球术技能
    me.msg("\n1. 学习火球术技能...")
    me.execute_cmd('learn fire.fireball')
    
    # 2. 创建测试目标
    from evennia import create_object
    from typeclasses.characters import Character
    
    if not hasattr(me.location.db, 'fireball_test_target'):
        target = create_object(Character, key="火球术测试木桩")
        target.location = me.location
        target.db.hp = 200
        target.db.max_hp = 200
        me.location.db.fireball_test_target = target
        me.msg(f"创建了测试目标: {target.key}")
    else:
        target = me.location.db.fireball_test_target
        target.db.hp = target.db.max_hp  # 重置HP
        me.msg(f"使用已有测试目标: {target.key}")
    
    me.msg(f"测试目标状态 - HP: {target.db.hp}/{target.db.max_hp}")
    
    # 3. 设置攻击目标
    me.msg("\n2. 设置攻击目标...")
    me.execute_cmd(f'hit {target.key}')
    
    # 4. 施放火球术
    me.msg("\n3. 施放火球术...")
    me.execute_cmd('cast fire.fireball')
    
    # 5. 显示结果
    me.msg("\n=== 测试结果 ===")
    me.msg(f"角色状态 - HP: {me.db.hp}/{me.db.max_hp}, MP: {me.db.mp}/{me.db.max_mp}")
    me.msg(f"测试目标状态 - HP: {target.db.hp}/{target.db.max_hp}")
    
    # 6. 显示技能列表
    me.msg("\n4. 技能列表:")
    me.execute_cmd('skills')
    
    me.msg("\n=== 火球术测试完成 ===")

def test_fireball_damage():
    """测试火球术伤害计算"""
    me = __import__('evennia').search_script('me').get()
    
    # 确保角色已学习火球术
    if "fire.fireball" not in me.db.skills:
        me.db.skills["fire.fireball"] = {"level": 1}
    
    # 创建测试目标
    from evennia import create_object
    from typeclasses.characters import Character
    
    target = create_object(Character, key="伤害测试木桩")
    target.location = me.location
    target.db.hp = 1000
    target.db.max_hp = 1000
    
    me.msg("=== 火球术伤害测试 ===")
    me.msg(f"测试目标初始HP: {target.db.hp}")
    
    # 设置目标并施放火球术
    me.db.target = target
    
    # 测试不同等级的火球术
    for level in [1, 3, 5]:
        me.db.skills["fire.fireball"]["level"] = level
        target.db.hp = target.db.max_hp  # 重置HP
        
        me.msg(f"\n测试等级 {level} 的火球术:")
        me.execute_cmd('cast fire.fireball')
        me.msg(f"目标剩余HP: {target.db.hp} (伤害: {target.db.max_hp - target.db.hp})")
    
    # 清理
    target.delete()
    me.msg("\n=== 伤害测试完成 ===")