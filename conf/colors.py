"""
全局颜色配置

定义游戏中各种元素的颜色
"""

# 定义颜色代码
# 使用Evennia的颜色标记，如 |r, |g, |y, |b, |m, |c, |w 等
# |n 表示重置颜色

class Colors:
    """全局颜色配置类"""
    
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
    
    @classmethod
    def format(cls, text, color_type):
        """格式化文本颜色
        
        Args:
            text (str): 要格式化的文本
            color_type (str): 颜色类型，对应Colors类中的属性
            
        Returns:
            str: 带颜色标记的文本
        """
        if hasattr(cls, color_type):
            color_code = getattr(cls, color_type)
            return f"{color_code}{text}{cls.RESET}"
        return text
    
    @classmethod
    def format_character_name(cls, name):
        """格式化角色名"""
        return cls.format(name, "CHARACTER_NAME")
    
    @classmethod
    def format_account_name(cls, name):
        """格式化账号名"""
        return cls.format(name, "ACCOUNT_NAME")
    
    @classmethod
    def format_room_name(cls, name):
        """格式化房间名"""
        return cls.format(name, "ROOM_NAME")
    
    @classmethod
    def format_exit_name(cls, name):
        """格式化出口名"""
        return cls.format(name, "EXIT_NAME")
