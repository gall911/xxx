"""
游戏主题系统

定义游戏中可用的颜色主题
"""

# Evennia颜色代码
# |r 红色, |g 绿色, |y 黄色, |b 蓝色, |m 洋红, |c 青色, |w 白色
# |x 黑色, |R 红色背景, |G 绿色背景, |Y 黄色背景
# |B 蓝色背景, |M 洋红背景, |C 青色背景, |W 白色背景
# |h 高亮, |u 下划线, |b 闪烁, |n 重置所有格式

class Theme:
    """主题基类，定义所有颜色属性"""
    
    # 基础颜色
    RESET = "|n"  # 重置颜色
    
    # 文本颜色
    NORMAL = "|n"  # 普通文本
    
    # 角色相关
    CHARACTER_NAME = "|y"  # 角色中文名
    CHARACTER_ALIAS = "|g"  # 角色别名
    
    # 账号相关
    ACCOUNT_NAME = "|c"  # 账号名
    
    # 房间相关
    ROOM_NAME = "|Y"  # 房间名（高亮黄色）
    ROOM_DESC = "|n"  # 房间描述
    
    # 出口相关
    EXIT_NAME = "|w"  # 出口名
    EXIT_ALIAS = "|g"  # 出口别名
    
    # 系统消息
    SYSTEM_MSG = "|R"  # 系统消息（红色）
    SUCCESS_MSG = "|G"  # 成功消息（绿色）
    ERROR_MSG = "|R"  # 错误消息（红色）
    
    # 对话相关
    SAY = "|C"  # 说话（青色）
    WHISPER = "|c"  # 悄悄话（淡青色）
    
    # 命令相关
    COMMAND = "|y"  # 命令提示

class DarkTheme(Theme):
    """暗色主题，适合夜间使用"""
    
    CHARACTER_NAME = "|c"  # 角色名改为青色
    ACCOUNT_NAME = "|C"  # 账号名改为亮青色
    ROOM_NAME = "|b"  # 房间名改为蓝色
    EXIT_NAME = "|w"  # 出口名保持白色
    SYSTEM_MSG = "|r"  # 系统消息改为暗红色
    SUCCESS_MSG = "|g"  # 成功消息改为绿色
    ERROR_MSG = "|R"  # 错误消息保持亮红色

class LightTheme(Theme):
    """亮色主题，适合白天使用"""
    
    CHARACTER_NAME = "|Y"  # 角色名改为亮黄色
    ACCOUNT_NAME = "|y"  # 账号名改为黄色
    ROOM_NAME = "|g"  # 房间名改为绿色
    EXIT_NAME = "|b"  # 出口名改为蓝色
    SYSTEM_MSG = "|R"  # 系统消息保持亮红色
    SUCCESS_MSG = "|G"  # 成功消息保持亮绿色
    ERROR_MSG = "|r"  # 错误消息改为暗红色

# 当前使用的主题
_current_theme = Theme

# 可用主题列表
THEMES = {
    "default": Theme,
    "dark": DarkTheme,
    "light": LightTheme,
}

def set_theme(theme_name):
    """设置当前主题
    
    Args:
        theme_name (str): 主题名称
        
    Returns:
        bool: 设置成功返回True，否则返回False
    """
    global _current_theme
    
    if theme_name in THEMES:
        _current_theme = THEMES[theme_name]
        return True
    return False

def get_current_theme():
    """获取当前主题类
    
    Returns:
        class: 当前主题类
    """
    return _current_theme

def get_available_themes():
    """获取所有可用主题列表
    
    Returns:
        list: 主题名称列表
    """
    return list(THEMES.keys())

def format_text(text, color_type):
    """格式化文本颜色
    
    Args:
        text (str): 要格式化的文本
        color_type (str): 颜色类型，对应Theme类中的属性
        
    Returns:
        str: 带颜色标记的文本
    """
    theme = get_current_theme()
    if hasattr(theme, color_type):
        color_code = getattr(theme, color_type)
        return f"{color_code}{text}{theme.RESET}"
    return text
