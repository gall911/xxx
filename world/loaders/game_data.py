# world/loaders/game_data.py
"""全局游戏数据存储 - 单例模式"""

# 游戏配置（从data/configs/加载）
CONFIG = {
    'game': {},
    'combat': {},
    'economy': {}
}

# 游戏内容数据（从data/加载）
GAME_DATA = {
    'realms': {},      # 境界配置
    'skills': {},      # 技能配置
    'items': {},       # 物品配置
    'affixes': {},     # 词条库
    'recipes': {},     # 合成配方
    'npcs': {},        # NPC配置
    'rooms': {},        # 房间配置
    'quests': {}   # 任务配置 
}

def get_config(key_path, default=None):
    """
    获取配置值，支持点号路径
    
    Args:
        key_path: 配置路径，如 'combat.turn_interval'
        default: 默认值
    
    Returns:
        配置值或默认值
    
    Example:
        >>> get_config('combat.turn_interval', 2.0)
        2.0
        >>> get_config('combat.critical_chance')
        0.05
    """
    keys = key_path.split('.')
    value = CONFIG
    
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
        else:
            return default
        
        if value is None:
            return default
    
    return value

def get_data(data_type, key):
    """
    获取游戏数据
    
    Args:
        data_type: 数据类型 ('items', 'skills', 'npcs' 等)
        key: 数据key
    
    Returns:
        数据字典或None
    
    Example:
        >>> get_data('items', '聚气丹')
        {'type': 'elixir', 'tier': 1, ...}
    """
    return GAME_DATA.get(data_type, {}).get(key)