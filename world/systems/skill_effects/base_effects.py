"""基础技能效果 - 伤害、治疗等"""
import random
from . import register_effect
from world.loaders.game_data import get_config

@register_effect("damage")
def damage_effect(config, attacker, target, context):
    """
    造成伤害效果
    
    Config参数:
        value: 基础伤害值
        element: 元素类型（可选）
        scale_with: 属性缩放（'strength', 'intelligence'等）
        scale_ratio: 缩放系数（默认1.0）
    """
    base_damage = config.get('value', 0)
    element = config.get('element', 'physical')
    
    # 属性缩放
    scale_attr = config.get('scale_with')
    scale_ratio = config.get('scale_ratio', 1.0)
    
    if scale_attr:
        attr_value = getattr(attacker.ndb, scale_attr, 0) or 0
        base_damage += attr_value * scale_ratio
    
    # 伤害浮动
    variance = get_config('combat.damage_variance', 0.1)
    damage = base_damage * random.uniform(1 - variance, 1 + variance)
    
    # 暴击倍率（从context获取）
    if context.get('is_critical'):
        crit_multi = get_config('combat.critical_multiplier', 2.0)
        damage *= crit_multi
    
    # 应用伤害
    final_damage = int(damage)
    target.ndb.hp = max(0, target.ndb.hp - final_damage)
    
    # 保存到上下文
    context['last_damage'] = final_damage
    context['total_damage'] = context.get('total_damage', 0) + final_damage
    
    return {
        'type': 'damage',
        'value': final_damage,
        'element': element,
    }

@register_effect("heal")
def heal_effect(config, attacker, target, context):
    """治疗效果"""
    heal_value = config.get('value', 0)
    heal_target_type = config.get('target', 'target')
    
    heal_target = attacker if heal_target_type == 'self' else target
    
    old_hp = heal_target.ndb.hp
    heal_target.ndb.hp = min(
        heal_target.ndb.hp + heal_value, 
        heal_target.ndb.max_hp
    )
    actual_heal = heal_target.ndb.hp - old_hp
    
    return {
        'type': 'heal',
        'value': actual_heal,
    }

@register_effect("restore_qi")
def restore_qi_effect(config, attacker, target, context):
    """恢复灵力效果"""
    qi_value = config.get('value', 0)
    
    old_qi = attacker.ndb.qi
    attacker.ndb.qi = min(
        attacker.ndb.qi + qi_value,
        attacker.ndb.max_qi
    )
    actual_restore = attacker.ndb.qi - old_qi
    
    return {
        'type': 'restore_qi',
        'value': actual_restore,
    }
