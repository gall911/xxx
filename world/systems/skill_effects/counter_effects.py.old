"""反击和反伤效果"""
from . import register_effect

@register_effect("counter_attack")
def counter_attack_effect(config, attacker, target, context):
    """反击效果（标记，实际执行在战斗系统）"""
    damage_ratio = config.get('damage_ratio', 0.5)
    
    return {
        'type': 'counter_attack',
        'damage_ratio': damage_ratio,
    }

@register_effect("damage_reflect")
def damage_reflect_effect(config, attacker, target, context):
    """反伤效果"""
    ratio = config.get('ratio', 0.2)
    
    last_damage = context.get('last_damage', 0)
    
    if last_damage <= 0:
        return {'type': 'damage_reflect', 'value': 0}
    
    reflect_damage = int(last_damage * ratio)
    
    # 对攻击者造成反伤
    target.ndb.hp = max(0, target.ndb.hp - reflect_damage)
    
    context['reflect_damage'] = reflect_damage
    
    return {
        'type': 'damage_reflect',
        'value': reflect_damage,
    }

@register_effect("damage_reduce")
def damage_reduce_effect(config, attacker, target, context):
    """减伤效果"""
    reduce_value = config.get('value', 5)
    
    # 这个效果应该在受到伤害前计算
    # 这里只是标记，实际减伤在伤害计算时处理
    
    return {
        'type': 'damage_reduce',
        'value': reduce_value,
    }
