#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
重新加载score命令
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

from evennia import ObjectDB
from commands.score_cmd import CmdScore

print("正在重新加载score命令...")

# 获取所有角色对象
characters = ObjectDB.objects.filter(db_typeclass_path__contains="characters")

# 为每个角色添加命令
for char in characters:
    try:
        char.cmdset.add_default(CmdScore)
        print(f"已为角色 '{char.key}' 添加score命令")
    except Exception as e:
        print(f"为角色 '{char.key}' 添加命令时出错: {e}")

print("score命令重新加载完成!")
