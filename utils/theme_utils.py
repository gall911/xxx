"""
主题工具模块

提供便捷的主题使用方法
"""

from conf.themes import format_text, get_current_theme

def color_text(text, color_type):
    """为文本添加颜色
    
    Args:
        text (str): 要着色的文本
        color_type (str): 颜色类型，对应Theme类中的属性
        
    Returns:
        str: 带颜色标记的文本
    """
    return format_text(text, color_type)

def color_character_name(name):
    """为角色名添加颜色"""
    return format_text(name, "CHARACTER_NAME")

def color_account_name(name):
    """为账号名添加颜色"""
    return format_text(name, "ACCOUNT_NAME")

def color_room_name(name):
    """为房间名添加颜色"""
    return format_text(name, "ROOM_NAME")

def color_exit_name(name):
    """为出口名添加颜色"""
    return format_text(name, "EXIT_NAME")

def color_system_msg(msg):
    """为系统消息添加颜色"""
    return format_text(msg, "SYSTEM_MSG")

def color_success_msg(msg):
    """为成功消息添加颜色"""
    return format_text(msg, "SUCCESS_MSG")

def color_error_msg(msg):
    """为错误消息添加颜色"""
    return format_text(msg, "ERROR_MSG")
