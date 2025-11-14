#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
僵尸NPC管理脚本
"""

import os
import sys

# 添加项目路径
sys.path.append('/home/gg/xxx')

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')

# 初始化Django
import django
django.setup()

from evennia.objects.models import ObjectDB

def find_zombie():
    """查找僵尸NPC"""
    # 查找所有NPC类型的对象
    npcs = ObjectDB.objects.filter(db_typeclass_path='typeclasses.npc.NPC')
    
    # 查找名为"僵尸"的NPC
    for npc in npcs:
        if npc.db_key == '僵尸':
            return npc
    
    return None

def set_zombie_invincible(state=True):
    """设置僵尸为无敌状态"""
    zombie = find_zombie()
    if not zombie:
        print("未找到僵尸NPC")
        return False
        
    # 设置无敌状态 (通过属性字典)
    zombie.attributes.add('is_invincible', state)
    
    if state:
        print("僵尸已设置为无敌状态")
    else:
        print("僵尸已取消无敌状态")
        
    return True

def show_zombie_status():
    """显示僵尸状态"""
    zombie = find_zombie()
    if not zombie:
        print("未找到僵尸NPC")
        return False
        
    # 获取属性值
    hp = zombie.attributes.get('hp', default=100)
    max_hp = zombie.attributes.get('max_hp', default=100)
    is_invincible = zombie.attributes.get('is_invincible', default=False)
    
    print(f"僵尸名称: {zombie.db_key}")
    print(f"僵尸ID: {zombie.id}")
    print(f"当前位置: {zombie.db_location}")
    print(f"HP: {hp}/{max_hp}")
    print(f"无敌状态: {'是' if is_invincible else '否'}")
    
    return True

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python manage_zombie.py status    - 显示僵尸状态")
        print("  python manage_zombie.py invincible - 设置僵尸为无敌")
        print("  python manage_zombie.py mortal    - 设置僵尸为可被击杀")
        return
        
    command = sys.argv[1]
    
    if command == 'status':
        show_zombie_status()
    elif command == 'invincible':
        set_zombie_invincible(True)
    elif command == 'mortal':
        set_zombie_invincible(False)
    else:
        print(f"未知命令: {command}")
        print("使用方法:")
        print("  python manage_zombie.py status    - 显示僵尸状态")
        print("  python manage_zombie.py invincible - 设置僵尸为无敌")
        print("  python manage_zombie.py mortal    - 设置僵尸为可被击杀")

if __name__ == "__main__":
    main()