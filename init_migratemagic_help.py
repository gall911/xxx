#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
初始化migratemagic命令的帮助条目
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

# 导入并执行帮助条目创建函数
from world.help_entries.migratemagic_help import add_migratemagic_help

print("正在初始化migratemagic命令的帮助条目...")
add_migratemagic_help()
print("帮助条目初始化完成!")
