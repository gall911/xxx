# world/systems/skill_effects/buff_effects.py
"""增益/减益效果 - Buff/Debuff"""
from . import register_effect

@register_effect("buff")
def buff_effect(config, attacker, target, context):
    """
    增益效果
    
    Config参数:
        target: 'self' 或 'target'
        attribute: 属性名称（'strength', 'agility'等）
        value: 增加值
        duration: 持续回合数
    """
    buff_target_type = config.get('target', 'self')
    attribute = config.get('attribute')
    value = config.get('value', 0)
    duration = config.get('duration', 3)
    
    if not attribute:
        return {
            'type': 'error',
            'message': 'buff效果缺少attribute参数'
        }
    
    # 确定目标
    buff_target = attacker if buff_target_type == 'self' else target
    
    # 初始化buff列表
    if not hasattr(buff_target.ndb, 'buffs'):
        buff_target.ndb.buffs = []
    
    # 添加buff
    buff_data = {
        'type': 'buff',
        'attribute': attribute,
        'value': value,
        'duration': duration,
        'remaining': duration
    }
    
    buff_target.ndb.buffs.append(buff_data)
    
    # 立即应用属性加成
    current_value = getattr(buff_target.ndb, attribute, 0)
    setattr(buff_target.ndb, attribute, current_value + value)
    
    return {
        'type': 'buff',
        'attribute': attribute,
        'value': value,
        'duration': duration,
        'message': f"{buff_target.key} 的 {attribute} 增加了 |y{value}|n (持续{duration}回合)"
    }

@register_effect("debuff")
def debuff_effect(config, attacker, target, context):
    """
    减益效果
    
    Config参数:
        attribute: 属性名称
        value: 减少值（正数）
        duration: 持续回合数
    """
    attribute = config.get('attribute')
    value = config.get('value', 0)
    duration = config.get('duration', 3)
    
    if not attribute:
        return {
            'type': 'error',
            'message': 'debuff效果缺少attribute参数'
        }
    
    # 初始化debuff列表
    if not hasattr(target.ndb, 'debuffs'):
        target.ndb.debuffs = []
    
    # 添加debuff
    debuff_data = {
        'type': 'debuff',
        'attribute': attribute,
        'value': value,
        'duration': duration,
        'remaining': duration
    }
    
    target.ndb.debuffs.append(debuff_data)
    
    # 立即应用属性减少
    current_value = getattr(target.ndb, attribute, 0)
    setattr(target.ndb, attribute, max(0, current_value - value))
    
    return {
        'type': 'debuff',
        'attribute': attribute,
        'value': value,
        'duration': duration,
        'message': f"{target.key} 的 {attribute} 降低了 |m{value}|n (持续{duration}回合)"
    }

@register_effect("remove_buff")
def remove_buff_effect(config, attacker, target, context):
    """
    移除增益效果（驱散）
    
    Config参数:
        count: 移除数量（默认1）
    """
    count = config.get('count', 1)
    
    if not hasattr(target.ndb, 'buffs') or not target.ndb.buffs:
        return {
            'type': 'remove_buff',
            'value': 0,
            'message': f"{target.key} 没有增益效果"
        }
    
    removed = 0
    for _ in range(min(count, len(target.ndb.buffs))):
        if target.ndb.buffs:
            buff = target.ndb.buffs.pop(0)
            # 移除属性加成
            attr = buff['attribute']
            value = buff['value']
            current = getattr(target.ndb, attr, 0)
            setattr(target.ndb, attr, max(0, current - value))
            removed += 1
    
    return {
        'type': 'remove_buff',
        'value': removed,
        'message': f"{attacker.key} 驱散了 {target.key} 的 {removed} 个增益效果"
    }

@register_effect("shield")
def shield_effect(config, attacker, target, context):
    """
    护盾效果 - 吸收伤害
    
    Config参数:
        value: 护盾值
        duration: 持续回合数
    """
    shield_value = config.get('value', 100)
    duration = config.get('duration', 5)
    
    shield_target = attacker if config.get('target') == 'self' else target
    
    # 初始化护盾
    if not hasattr(shield_target.ndb, 'shield'):
        shield_target.ndb.shield = 0
    
    shield_target.ndb.shield += shield_value
    shield_target.ndb.shield_duration = duration
    
    return {
        'type': 'shield',
        'value': shield_value,
        'duration': duration,
        'message': f"{shield_target.key} 获得了 |c{shield_value}|n 点护盾 (持续{duration}回合)"
    }

@register_effect("dot")
def dot_effect(config, attacker, target, context):
    """
    持续伤害效果 (Damage Over Time)
    
    Config参数:
        value: 每回合伤害
        duration: 持续回合数
        element: 元素类型
    """
    damage_per_turn = config.get('value', 10)
    duration = config.get('duration', 3)
    element = config.get('element', 'physical')
    
    # 初始化DOT列表
    if not hasattr(target.ndb, 'dots'):
        target.ndb.dots = []
    
    # 添加DOT效果
    dot_data = {
        'type': 'dot',
        'damage': damage_per_turn,
        'duration': duration,
        'remaining': duration,
        'element': element,
        'source': attacker.key
    }
    
    target.ndb.dots.append(dot_data)
    
    return {
        'type': 'dot',
        'value': damage_per_turn,
        'duration': duration,
        'element': element,
        'message': f"{target.key} 中了 {element} 系持续伤害，每回合受到 {damage_per_turn} 点伤害"
    }