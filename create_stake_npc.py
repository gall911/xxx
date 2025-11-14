#!/usr/bin/env python
"""
创建木桩NPC的脚本
"""

import os
import sys

# 添加项目路径
sys.path.insert(0, '/home/gg/xxx')

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')
import django
django.setup()

# 初始化Evennia
import evennia
evennia._init()

from evennia.utils.create import create_object
from typeclasses.npc import NPC

def create_stake_npc():
    """创建木桩NPC"""
    # 创建一个简单的房间作为临时位置
    from typeclasses.rooms import Room
    temp_room = create_object(Room, key="临时房间")
    
    # 创建木桩NPC
    stake_npc = create_object(NPC, key="木桩", location=temp_room)
    
    # 设置别名
    stake_npc.aliases.add("mz")
    
    # 设置初始属性
    stake_npc.db.hp = 100
    stake_npc.db.max_hp = 100
    stake_npc.db.is_invincible = True  # 设置为无敌
    
    print(f"成功创建木桩NPC: {stake_npc.key} ({stake_npc.aliases.all()[0]})")
    print(f"位置: {stake_npc.location.key}")
    print(f"HP: {stake_npc.db.hp}/{stake_npc.db.max_hp}")
    print(f"无敌状态: {stake_npc.db.is_invincible}")
    
    return stake_npc

if __name__ == "__main__":
    create_stake_npc()