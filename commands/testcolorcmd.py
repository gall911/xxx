"""
测试颜色系统命令

使用方法: testcolor
"""

from evennia import Command
from utils.color_utils import (
    color_character_name,
    color_account_name,
    color_room_name,
    color_exit_name,
    color_system_msg,
    color_success_msg,
    color_error_msg
)

class CmdTestColor(Command):
    """
    测试颜色系统
    
    使用方法:
        testcolor
    """
    
    key = "testcolor"
    help_category = "系统"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        caller.msg("颜色系统测试:")
        caller.msg("-" * 40)
        
        # 测试角色名颜色
        caller.msg(f"角色名: {color_character_name('张三')}")
        
        # 测试账号名颜色
        caller.msg(f"账号名: {color_account_name('player1')}")
        
        # 测试房间名颜色
        caller.msg(f"房间名: {color_room_name('新手村')}")
        
        # 测试出口名颜色
        caller.msg(f"出口名: {color_exit_name('north')}")
        
        # 测试系统消息颜色
        caller.msg(f"系统消息: {color_system_msg('系统提示: 欢迎来到游戏！')}")
        
        # 测试成功消息颜色
        caller.msg(f"成功消息: {color_success_msg('操作成功！')}")
        
        # 测试错误消息颜色
        caller.msg(f"错误消息: {color_error_msg('错误: 无效的命令！')}")
        
        caller.msg("-" * 40)
        caller.msg("测试完成！")
