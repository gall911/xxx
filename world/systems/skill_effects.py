"""
world/systems/skill_effects.py
技能效果注册与分发器
"""
from evennia.utils import logger

# 效果注册表
_EFFECTS = {}

def register_effect(name):
    """装饰器：注册技能效果处理函数"""
    def decorator(func):
        _EFFECTS[name] = func
        return func
    return decorator

def apply_effect(effect_config, attacker, target, context):
    """
    分发并执行具体的技能效果
    
    Args:
        effect_config (dict): 技能配置中的 effect 条目
        attacker (Object): 攻击者
        target (Object): 目标
        context (dict): 战斗上下文（用于传递伤害统计、暴击状态等）
    """
    effect_type = effect_config.get('type')
    handler = _EFFECTS.get(effect_type)
    
    if not handler:
        logger.log_err(f"[战斗] 未知的技能效果类型: {effect_type}")
        return None
        
    try:
        # 调用具体的处理函数（如 damage_effect）
        return handler(effect_config, attacker, target, context)
    except Exception as e:
        logger.log_trace(f"[战斗] 执行效果 {effect_type} 时出错: {e}")
        return None