# world/loaders/skill_loader.py
"""技能加载器 - 支持继承和等级计算"""
from copy import deepcopy
from world.loaders.game_data import GAME_DATA, get_data

def calculate_skill_stats(skill_config, level):
    """
    根据技能配置和等级计算属性
    支持两种公式：
    1. per_level: base + (level * per_level)
    2. grow: base * (1 + grow)^level
    
    Args:
        skill_config (dict): 技能配置
        level (int): 技能等级
    
    Returns:
        dict: 计算后的属性
    """
    if 'level_formula' not in skill_config:
        return {}
    
    scaling = skill_config['level_formula']
    result = {}
    
    for stat_name, formula in scaling.items():
        if stat_name == 'max_level':
            continue
        
        if isinstance(formula, dict):
            base = formula.get('base', 0)
            per_level = formula.get('per_level', 0)
            grow = formula.get('grow', 0)
            min_val = formula.get('min', None)
            max_val = formula.get('max', None)
            
            # 计算公式选择
            if grow > 0:
                # 指数成长：base * (1 + grow)^level
                value = base * ((1 + grow) ** level)
            elif per_level != 0:
                # 线性成长：base + (level * per_level)
                value = base + (level * per_level)
            else:
                # 固定值
                value = base
            
            # 应用上下限
            if min_val is not None:
                value = max(value, min_val)
            if max_val is not None:
                value = min(value, max_val)
            
            # 整数属性取整
            if stat_name in ['cooldown', 'cost_qi', 'damage', 'tick_damage']:
                value = int(value)
            
            result[stat_name] = value
        else:
            result[stat_name] = formula
    
    return result

def get_skill_at_level(skill_key, level):
    """
    获取指定等级的技能配置
    
    Args:
        skill_key (str): 技能key
        level (int): 技能等级
    
    Returns:
        dict: 完整的技能配置（包含计算后的属性）
    """
    base_config = GAME_DATA['skills'].get(skill_key)
    if not base_config:
        return None
    
    # 深拷贝，避免修改原始配置
    config = deepcopy(base_config)
    
    # 计算等级属性
    if 'level_formula' in config:
        level_stats = calculate_skill_stats(config, level)
        
        # 合并到配置中
        for stat_name, value in level_stats.items():
            config[stat_name] = value
        
        # 处理effects中的占位符
        if 'effects' in config:
            for effect in config['effects']:
                for key, val in effect.items():
                    if isinstance(val, str) and val.startswith('{level_'):
                        stat_key = val[7:-1]  # 去掉 {level_ 和 }
                        if stat_key in level_stats:
                            effect[key] = level_stats[stat_key]
    
    return config