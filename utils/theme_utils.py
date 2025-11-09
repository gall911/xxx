"""
主题工具模块

提供便捷的主题使用方法
"""

from server.conf.theme import format_text

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
    from server.conf.theme import CHARACTER_NAME
    return f"{CHARACTER_NAME}{name}|n"

def color_account_name(name):
    """为账号名添加颜色"""
    from server.conf.theme import ACCOUNT_NAME
    return f"{ACCOUNT_NAME}{name}|n"

def color_room_name(name):
    """为房间名添加颜色"""
    from server.conf.theme import ROOM_NAME
    return f"{ROOM_NAME}{name}|n"

def color_exit_name(name):
    """为出口名添加颜色"""
    from server.conf.theme import EXIT_NAME
    return f"{EXIT_NAME}{name}|n"

def color_system_msg(msg):
    """为系统消息添加颜色"""
    from server.conf.theme import SYSTEM_MSG
    return f"{SYSTEM_MSG}{msg}|n"

def color_success_msg(msg):
    """为成功消息添加颜色"""
    from server.conf.theme import SUCCESS_MSG
    return f"{SUCCESS_MSG}{msg}|n"

def color_error_msg(msg):
    """为错误消息添加颜色"""
    from server.conf.theme import ERROR_MSG
    return f"{ERROR_MSG}{msg}|n"
