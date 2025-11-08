#!/usr/bin/env python
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')
django.setup()

from commands.default_cmdsets import CharacterCmdSet
from evennia import default_cmds

# 创建自定义命令类
class CmdLsRoom(default_cmds.CmdLook):
    """
    查看房间 - 简短别名

    用法:
      lsroom
      lr
    """
    key = "lsroom"
    aliases = ["lr"]

    def func(self):
        # 调用原始的look命令功能
        default_cmds.CmdLook.func(self)

class CmdLsExit(default_cmds.CmdExits):
    """
    查看出口 - 简短别名

    用法:
      lsexit
      le
    """
    key = "lsexit"
    aliases = ["le"]

    def func(self):
        # 调用原始的exits命令功能
        default_cmds.CmdExits.func(self)

class CmdLsAccount(default_cmds.CmdWho):
    """
    查看在线账号 - 简短别名

    用法:
      lsaccount
      la
    """
    key = "lsaccount"
    aliases = ["la"]

    def func(self):
        # 调用原始的who命令功能
        default_cmds.CmdWho.func(self)

# 添加命令到默认命令集
def add_command_aliases():
    # 获取当前命令集
    cmdset = CharacterCmdSet

    # 添加新的命令
    cmdset.add(CmdLsRoom)
    cmdset.add(CmdLsExit)
    cmdset.add(CmdLsAccount)

    print("已成功添加命令别名:")
    print("- lsroom/lr: 查看房间")
    print("- lsexit/le: 查看出口")
    print("- lsaccount/la: 查看在线账号")

if __name__ == "__main__":
    add_command_aliases()
