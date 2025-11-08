"""
颜色工具模块

提供便捷的颜色使用方法
"""

from conf.colors import Colors

def color_text(text, color_type):
    """为文本添加颜色
    
    Args:
        text (str): 要着色的文本
        color_type (str): 颜色类型，对应Colors类中的属性
        
    Returns:
        str: 带颜色标记的文本
    """
    return Colors.format(text, color_type)

def color_character_name(name):
    """为角色名添加颜色"""
    return Colors.format_character_name(name)

def color_account_name(name):
    """为账号名添加颜色"""
    return Colors.format_account_name(name)

def color_room_name(name):
    """为房间名添加颜色"""
    return Colors.format_room_name(name)

def color_exit_name(name):
    """为出口名添加颜色"""
    return Colors.format_exit_name(name)

def color_system_msg(msg):
    """为系统消息添加颜色"""
    return Colors.format(msg, "SYSTEM_MSG")

def color_success_msg(msg):
    """为成功消息添加颜色"""
    return Colors.format(msg, "SUCCESS_MSG")

def color_error_msg(msg):
    """为错误消息添加颜色"""
    return Colors.format(msg, "ERROR_MSG")
