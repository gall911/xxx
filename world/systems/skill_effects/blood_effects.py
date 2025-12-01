"""血系技能效果"""
from . import register_effect

@register_effect("lifesteal")
def lifesteal_effect(config, attacker, target, context):
    """吸血效果"""
    ratio = config.get('ratio', 0.5)
    
    last_damage = context.get('last_damage', 0)
    
    if last_damage <= 0:
        return {'type': 'lifesteal', 'value': 0}
    
    lifesteal_amount = int(last_damage * ratio)
    
    old_hp = attacker.ndb.hp
    attacker.ndb.hp = min(
        attacker.ndb.hp + lifesteal_amount,
        attacker.ndb.max_hp
    )
    actual_heal = attacker.ndb.hp - old_hp
    
    # 保存到上下文
    context['total_heal'] = context.get('total_heal', 0) + actual_heal
    
    return {
        'type': 'lifesteal',
        'value': actual_heal,
    }
