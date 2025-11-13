#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
初始化score命令到默认命令集
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

# 导入默认命令集
from commands.default_cmdsets import CharacterCmdSet

# 添加score命令
try:
    from commands.score_cmd import CmdScore
    CharacterCmdSet.score_cmd = CmdScore
    print("已将score命令添加到默认命令集")
except Exception as e:
    print(f"添加score命令时出错: {e}")
