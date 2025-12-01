# world/loaders/validator.py
"""数据验证器 - 检查YAML数据完整性"""
from evennia.utils import logger

def validate_skill(skill_key, skill_data):
    """验证技能数据"""
    required_fields = ['name', 'effects']
    
    for field in required_fields:
        if field not in skill_data:
            logger.log_warn(f"[验证] 技能 '{skill_key}' 缺少字段: {field}")
            return False
    
    # 验证效果列表
    if not isinstance(skill_data['effects'], list):
        logger.log_warn(f"[验证] 技能 '{skill_key}' 的effects必须是列表")
        return False
    
    for effect in skill_data['effects']:
        if 'type' not in effect:
            logger.log_warn(f"[验证] 技能 '{skill_key}' 的效果缺少type字段")
            return False
    
    return True

def validate_item(item_key, item_data):
    """验证物品数据"""
    required_fields = ['name', 'type']
    
    for field in required_fields:
        if field not in item_data:
            logger.log_warn(f"[验证] 物品 '{item_key}' 缺少字段: {field}")
            return False
    
    return True

def validate_all_data(game_data):
    """
    验证所有游戏数据
    
    Args:
        game_data: GAME_DATA字典
    
    Returns:
        tuple: (是否通过, 错误列表)
    """
    errors = []
    
    # 验证技能
    for skill_key, skill_data in game_data.get('skills', {}).items():
        if not validate_skill(skill_key, skill_data):
            errors.append(f"技能验证失败: {skill_key}")
    
    # 验证物品
    for item_key, item_data in game_data.get('items', {}).items():
        if not validate_item(item_key, item_data):
            errors.append(f"物品验证失败: {item_key}")
    
    if errors:
        logger.log_warn(f"[验证] 发现 {len(errors)} 个数据问题")
        for error in errors:
            logger.log_warn(f"  - {error}")
        return False, errors
    
    logger.log_info("[验证] 所有数据验证通过")
    return True, []