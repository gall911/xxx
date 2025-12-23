"""技能效果插件注册中心"""

EFFECT_REGISTRY = {}

def register_effect(effect_type):
    """注册效果"""
    def decorator(func):
        EFFECT_REGISTRY[effect_type] = func
        return func
    return decorator

def apply_effect(effect_config, attacker, target, context):
    """应用效果"""
    effect_type = effect_config.get('type')
    
    if not effect_type:
        return {'type': 'error', 'message': '缺少type字段'}
    
    handler = EFFECT_REGISTRY.get(effect_type)
    
    if not handler:
        return {'type': 'error', 'message': f'未知效果: {effect_type}'}
    
    try:
        return handler(effect_config, attacker, target, context)
    except Exception as e:
        return {'type': 'error', 'message': f'执行错误: {e}'}

def get_registered_effects():
    """获取已注册效果列表"""
    return list(EFFECT_REGISTRY.keys())

# ========== 导入所有效果模块 ==========
from . import base_effects
from . import buff_effects
from . import debuff_effects
# 删除：blood_effects, counter_effects
__all__ = [
    'register_effect',
    'apply_effect',
    'get_registered_effects',
    'EFFECT_REGISTRY'
]