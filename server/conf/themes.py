"""
主题配置模块

定义游戏中的各种颜色主题
"""

# 默认主题颜色配置
DEFAULT_THEME = {
    "character_name": "|c",
    "account_name": "|c",
    "room_name": "|y",
    "exit_name": "|g",
    "system_msg": "|w",
    "success_msg": "|g",
    "error_msg": "|r"
}

# 当前使用的主题
_current_theme = DEFAULT_THEME

def set_theme(theme_name):
    """设置主题
    
    Args:
        theme_name (str): 主题名称
        
    Returns:
        bool: 是否成功设置主题
    """
    global _current_theme
    
    # 目前只有默认主题
    if theme_name.lower() == "default":
        _current_theme = DEFAULT_THEME
        return True
        
    return False

def get_current_theme():
    """获取当前主题
    
    Returns:
        dict: 当前主题配置
    """
    return _current_theme

def get_available_themes():
    """获取所有可用主题
    
    Returns:
        list: 可用主题名称列表
    """
    return ["default"]
