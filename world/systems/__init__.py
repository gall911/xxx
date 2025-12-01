# world/systems/skill_effects/__init__.py
"""技能效果插件注册中心"""

# 全局效果注册表
EFFECT_REGISTRY = {}

def register_effect(effect_type):
    """装饰器：注册技能效果"""
    def decorator(func):
        EFFECT_REGISTRY[effect_type] = func
        return func
    return decorator

def apply_effect(effect_config, attacker, target, combat_context):
    """应用技能效果"""
    effect_type = effect_config['type']
    handler = EFFECT_REGISTRY.get(effect_type)
    
    if not handler:
        print(f"警告：未找到效果类型 {effect_type}")
        return None
    
    return handler(effect_config, attacker, target, combat_context)