# 临时修复，替换 commands/combat.py 的 _create_bar 方法

def _create_bar(self, current, maximum, length, filled_color, empty_color):
    """创建进度条"""
    # 防止 None 值
    if current is None:
        current = 0
    if maximum is None or maximum == 0:
        maximum = 1
    
    filled = int((current / maximum) * length)
    empty = length - filled
    bar = filled_color + "█" * filled + empty_color + "░" * empty + "|n"
    return bar
