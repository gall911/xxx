"""
全局主题设置

定义游戏中使用的颜色
"""

# Evennia颜色代码
# |r 红色, |g 绿色, |y 黄色, |b 蓝色, |m 洋红, |c 青色, |w 白色
# |x 黑色, |R 红色背景, |G 绿色背景, |Y 黄色背景
# |B 蓝色背景, |M 洋红背景, |C 青色背景, |W 白色背景
# |h 高亮, |u 下划线, |b 闪烁, |n 重置所有格式

# 角色相关
CHARACTER_NAME = "|420"  # 角色名颜色
#CHARACTER_ALIAS = "|155"  # 角色别名颜色

# 账号相关
ACCOUNT_NAME = "|[022"  # 账号名颜色

# 房间相关
ROOM_NAME = "|055"  # 房间名颜色
ROOM_DESC = "|n"  # 房间描述颜色

# 出口相关
EXIT_NAME = "|535"  # 出口名颜色
EXIT_ALIAS = "|g"  # 出口别名颜色

# 系统消息
SYSTEM_MSG = "|R"  # 系统消息颜色
SUCCESS_MSG = "|g"  # 成功消息颜色
ERROR_MSG = "|r"  # 错误消息颜色

# 对话相关
SAY = "|C"  # 说话颜色
WHISPER = "|c"  # 悄悄话颜色

# 命令相关
COMMAND = "|y"  # 命令提示颜色

def format_text(text, color_type):
    """格式化文本颜色
    
    Args:
        text (str): 要格式化的文本
        color_type (str): 颜色类型
        
    Returns:
        str: 带颜色标记的文本
    """
    color_code = globals().get(color_type, "|n")
    return f"{color_code}{text}|n"