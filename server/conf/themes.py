"""
主题配置模块

定义游戏中的各种颜色主题
"""

# 默认主题颜色配置
DEFAULT_THEME = {
    "character_name": "|c",
    "account_name": "|522",
    "room_name": "|y",
    "exit_name": "|g",
    "system_msg": "|w",
    "success_msg": "|g",
    "error_msg": "|r"
}

# 暗色主题
DARK_THEME = {
    "character_name": "|M",
    "account_name": "|M",
    "room_name": "|m",
    "exit_name": "|C",
    "system_msg": "|W",
    "success_msg": "|G",
    "error_msg": "|R"
}

# 明亮主题
BRIGHT_THEME = {
    "character_name": "|Y",
    "account_name": "|Y",
    "room_name": "|R",
    "exit_name": "|G",
    "system_msg": "|W",
    "success_msg": "|G",
    "error_msg": "|R"
}

# 简约主题
MINIMAL_THEME = {
    "character_name": "|n",
    "account_name": "|n",
    "room_name": "|n",
    "exit_name": "|n",
    "system_msg": "|n",
    "success_msg": "|n",
    "error_msg": "|n"
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
    
    # 根据主题名称设置主题
    theme_name = theme_name.lower()
    if theme_name == "default":
        _current_theme = DEFAULT_THEME
        return True
    elif theme_name == "dark":
        _current_theme = DARK_THEME
        return True
    elif theme_name == "bright":
        _current_theme = BRIGHT_THEME
        return True
    elif theme_name == "minimal":
        _current_theme = MINIMAL_THEME
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
    return ["default", "dark", "bright", "minimal"]
