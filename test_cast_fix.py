#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import django

# 添加项目路径
sys.path.insert(0, '/home/gg/xxx')

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')
django.setup()

# 导入必要的模块
from typeclasses.spells.loader import load_spell_data

def test_spell_loading():
    """测试技能加载"""
    print("测试技能加载...")
    
    # 测试完整键名
    spell_keys = [
        "fire.fireball",
        "ice.iceball", 
        "fire.fb"
    ]
    
    for spell_key in spell_keys:
        print(f"\n测试加载技能: {spell_key}")
        data = load_spell_data(spell_key)
        if data:
            print(f"  成功加载!")
            print(f"  名称: {data.get('name', '未知')}")
            print(f"  描述: {data.get('desc', '无描述')}")
        else:
            print(f"  加载失败!")

if __name__ == "__main__":
    test_spell_loading()