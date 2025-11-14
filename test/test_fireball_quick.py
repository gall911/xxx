#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
快速测试火球术

使用方法：
1. 在游戏中运行: @py import test_fireball; test_fireball.quick_test()
"""

def quick_test():
    """快速测试火球术"""
    me = __import__('evennia').search_script('me').get()
    
    # 初始化角色
    me.db.skills = {}
    me.db.hp = 100
    me.db.max_hp = 100
    me.db.mp = 100
    me.db.max_mp = 100
    
    # 学习火球术
    me.execute_cmd('learn fire.fireball')
    
    # 创建测试目标
    from evennia import create_object
    from typeclasses.characters import Character
    
    target = create_object(Character, key="火球测试木桩")
    target.location = me.location
    target.db.hp = 200
    target.db.max_hp = 200
    
    # 设置目标并施放火球术
    me.execute_cmd(f'hit {target.key}')
    me.execute_cmd('cast fire.fireball')
    
    # 显示结果
    me.msg(f"目标HP: {target.db.hp}/{target.db.max_hp}")
    me.execute_cmd('skills')
    
    # 清理
    target.delete()