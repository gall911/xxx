#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
初始化修仙风格命令集
"""

import os
import sys

# 添加项目路径到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 设置Django环境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.conf.settings")

# 初始化Django
import django
django.setup()

# 导入并添加命令集
from commands.xianya.xianya_cmdset import XianyaCmdSet
from evennia import ObjectDB

print("正在初始化修仙风格命令集...")

# 获取所有角色对象
characters = ObjectDB.objects.filter(db_typeclass_path__contains="characters")

# 为每个角色添加命令集
for char in characters:
    try:
        char.cmdset.add_default(XianyaCmdSet)
        print(f"已为角色 '{char.key}' 添加修仙风格命令集")
    except Exception as e:
        print(f"为角色 '{char.key}' 添加命令集时出错: {e}")

print("修仙风格命令集初始化完成!")
