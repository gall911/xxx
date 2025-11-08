#!/usr/bin/env python
"""测试命令集是否正确加载"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')
django.setup()

from commands.default_cmdsets import CharacterCmdSet
from evennia import default_cmds

print("=" * 50)
print("测试 CharacterCmdSet")
print("=" * 50)

# 创建命令集实例
cmdset = CharacterCmdSet()
cmdset.at_cmdset_creation()

# 获取所有命令
commands = cmdset.commands
print(f"\n总共加载了 {len(commands)} 个命令\n")

# 查找 look 命令
look_found = False
l_found = False
ls_found = False

for cmd in commands:
    if hasattr(cmd, 'key'):
        if cmd.key == 'look':
            look_found = True
            print(f"✓ 找到 look 命令: {cmd}")
        if cmd.key == 'l':
            l_found = True
            print(f"✓ 找到 l 命令: {cmd}")
        if cmd.key == 'ls':
            ls_found = True
            print(f"✓ 找到 ls 命令: {cmd}")
            
# 列出所有命令的 key
print("\n所有命令的 key:")
for cmd in commands:
    if hasattr(cmd, 'key'):
        aliases = getattr(cmd, 'aliases', [])
        print(f"  - {cmd.key} (aliases: {aliases})")

print("\n" + "=" * 50)
if look_found:
    print("✓ look 命令已加载")
else:
    print("✗ look 命令未找到！")

if l_found:
    print("✓ l 命令已加载")
else:
    print("✗ l 命令未找到！")

if ls_found:
    print("✓ ls 命令已加载")
else:
    print("✗ ls 命令未找到！")
print("=" * 50)

