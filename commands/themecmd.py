"""
主题管理命令

使用方法:
    theme list - 列出所有可用主题
    theme current - 显示当前主题
    theme set [主题名] - 设置主题
    theme test - 测试当前主题颜色
"""

from evennia import Command
from server.conf.themes import set_theme, get_current_theme, get_available_themes
from utils.theme_utils import (
    color_character_name,
    color_account_name,
    color_room_name,
    color_exit_name,
    color_system_msg,
    color_success_msg,
    color_error_msg
)
from utils.theme_hooks import apply_theme_to_all_objects

class CmdTheme(Command):
    """
    主题管理命令
    
    使用方法:
        theme list - 列出所有可用主题
        theme current - 显示当前主题
        theme set [主题名] - 设置主题
        theme test - 测试当前主题颜色
        theme apply - 将当前主题应用到所有现有对象
    """
    
    key = "theme"
    help_category = "系统"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        if not self.args or self.args == "current":
            # 显示当前主题
            current = "default"
            caller.msg(f"当前主题: {current}")
            return
            
        args = self.args.strip().lower()
        
        if args == "list":
            # 列出所有可用主题
            themes = get_available_themes()
            current = "default"
            caller.msg("可用主题:")
            for theme in themes:
                if theme.lower() == current.lower():
                    theme_name = f"{theme} (当前)"
                else:
                    theme_name = theme
                caller.msg(f"- {theme_name}")
            return
            
        if args == "test":
            # 测试当前主题颜色
            caller.msg("主题颜色测试:")
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
            return
            
        if args.startswith("set "):
            # 设置主题
            theme_name = args[4:].strip()
            if set_theme(theme_name):
                caller.msg(f"主题已设置为: {theme_name}")
            else:
                caller.msg(f"未知主题: {theme_name}")
                themes = get_available_themes()
                caller.msg(f"可用主题: {', '.join(themes)}")
            return
            
        if args == "apply":
            # 将当前主题应用到所有现有对象
            caller.msg("正在应用主题到所有对象...")
            count = apply_theme_to_all_objects()
            caller.msg(f"已将当前主题应用到 {count} 个对象。")
            return
            
        # 默认显示帮助
        caller.msg("用法:")
        caller.msg("  theme list - 列出所有可用主题")
        caller.msg("  theme current - 显示当前主题")
        caller.msg("  theme set [主题名] - 设置主题")
        caller.msg("  theme test - 测试当前主题颜色")
        caller.msg("  theme apply - 将当前主题应用到所有现有对象")
