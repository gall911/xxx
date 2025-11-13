#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
将score命令添加到默认命令集
"""

import os
import sys

# 添加项目路径到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 读取默认命令集文件
with open('commands/default_cmdsets.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 查找要插入的位置
insert_pos = content.find('# 添加魔法命令')

if insert_pos == -1:
    print("无法找到插入位置")
    sys.exit(1)

# 构建要插入的代码
code_to_insert = """        # 添加修仙风格的状态命令
        try:
            from commands.score_cmd import CmdScore
            self.add(CmdScore)
            print("已添加修仙风格状态命令")
        except Exception as e:
            import traceback
            import sys
            print(f"Warning: Could not add score command: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)

"""

# 插入代码
new_content = content[:insert_pos] + code_to_insert + content[insert_pos:]

# 写回文件
with open('commands/default_cmdsets.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("已将score命令添加到默认命令集")
