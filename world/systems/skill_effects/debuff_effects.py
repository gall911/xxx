"""
world/systems/skill_effects/debuff_effects.py
减益效果（Debuff）- 修仙MUD
"""
from . import register_effect
from world.systems.buff_manager import BuffManager

@register_effect("apply_poison")
def apply_poison_effect(config, attacker, target, context):
    """
    中毒：每回合损失生命
    
    Config:
        tick_damage: 每回合伤害
        duration: 持续回合数
        element: 元素类型（默认poison）
    """
    tick_damage = config.get('tick_damage', 10)
    duration = config.get('duration', 3)
    element = config.get('element', 'poison')
    name = config.get('name', '中毒')
    
    buff_config = {
        'type': 'dot',
        'name': name,
        'duration': duration,
        'max_stacks': 5,
        'stack_mode': 'add',
        'effects': [
            {'type': 'damage', 'value': tick_damage, 'element': element}
        ],
        'trigger_on': 'turn_start',
        'tick_interval': 1,
        'show_tick_message': True,
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_poison',
        'tick_damage': tick_damage,
    }

@register_effect("apply_weakness")
def apply_weakness_effect(config, attacker, target, context):
    """
    虚弱：降低攻击力
    
    Config:
        value: 攻击力减少量
        duration: 持续回合数
        stat: 属性名（strength/intelligence等）
    """
    debuff_value = config.get('value', -10)
    duration = config.get('duration', 3)
    stat = config.get('stat', 'strength')
    name = config.get('name', '虚弱')
    
    buff_config = {
        'type': 'debuff',
        'name': name,
        'duration': duration,
        'max_stacks': 3,
        'stack_mode': 'add',
        'effects': [
            {'type': 'stat_mod', 'stat': stat, 'value': debuff_value}
        ],
        'trigger_on': 'turn_start',
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_weakness',
        'value': debuff_value,
    }

@register_effect("apply_armor_break")
def apply_armor_break_effect(config, attacker, target, context):
    """
    破防：降低防御力
    
    Config:
        value: 防御力减少量
        duration: 持续回合数
    """
    debuff_value = config.get('value', -15)
    duration = config.get('duration', 3)
    name = config.get('name', '破防')
    
    buff_config = {
        'type': 'debuff',
        'name': name,
        'duration': duration,
        'max_stacks': 3,
        'stack_mode': 'add',
        'effects': [
            {'type': 'stat_mod', 'stat': 'defense', 'value': debuff_value}
        ],
        'trigger_on': 'turn_start',
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_armor_break',
        'value': debuff_value,
    }

@register_effect("apply_slow")
def apply_slow_effect(config, attacker, target, context):
    """
    减速：降低行动速度
    
    Config:
        value: 敏捷减少量
        duration: 持续回合数
    """
    debuff_value = config.get('value', -5)
    duration = config.get('duration', 3)
    name = config.get('name', '减速')
    
    buff_config = {
        'type': 'debuff',
        'name': name,
        'duration': duration,
        'max_stacks': 3,
        'stack_mode': 'add',
        'effects': [
            {'type': 'stat_mod', 'stat': 'agility', 'value': debuff_value}
        ],
        'trigger_on': 'turn_start',
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_slow',
        'value': debuff_value,
    }

@register_effect("apply_bleed")
def apply_bleed_effect(config, attacker, target, context):
    """
    流血：每回合损失生命 + 治疗效果降低
    
    Config:
        tick_damage: 每回合伤害
        heal_reduce: 治疗效果降低比例（0.5 = 50%）
        duration: 持续回合数
    """
    tick_damage = config.get('tick_damage', 15)
    heal_reduce = config.get('heal_reduce', 0.5)
    duration = config.get('duration', 3)
    name = config.get('name', '流血')
    
    buff_config = {
        'type': 'dot',
        'name': name,
        'duration': duration,
        'max_stacks': 5,
        'stack_mode': 'add',
        'effects': [
            {'type': 'damage', 'value': tick_damage, 'element': 'physical'}
        ],
        'trigger_on': 'turn_start',
        'tick_interval': 1,
        'show_tick_message': True,
        'extra': {
            'heal_reduce': heal_reduce,
        }
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_bleed',
        'tick_damage': tick_damage,
    }

@register_effect("apply_silence")
def apply_silence_effect(config, attacker, target, context):
    """
    沉默：无法使用技能
    
    Config:
        duration: 持续回合数
    """
    duration = config.get('duration', 2)
    name = config.get('name', '沉默')
    
    buff_config = {
        'type': 'control',
        'name': name,
        'duration': duration,
        'max_stacks': 1,
        'stack_mode': 'refresh',
        'effects': [],
        'trigger_on': 'turn_start',
        'extra': {
            'silenced': True,
        }
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_silence',
    }

@register_effect("apply_stun")
def apply_stun_effect(config, attacker, target, context):
    """
    禁锢/眩晕：无法行动
    
    Config:
        duration: 持续回合数
    """
    duration = config.get('duration', 1)
    name = config.get('name', '禁锢')
    
    buff_config = {
        'type': 'control',
        'name': name,
        'duration': duration,
        'max_stacks': 1,
        'stack_mode': 'refresh',
        'effects': [],
        'trigger_on': 'turn_start',
        'extra': {
            'stunned': True,
        }
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_stun',
    }

@register_effect("apply_blind")
def apply_blind_effect(config, attacker, target, context):
    """
    致盲：攻击命中率下降
    
    Config:
        value: 命中率减少量（-0.2 = -20%）
        duration: 持续回合数
    """
    debuff_value = config.get('value', -0.2)
    duration = config.get('duration', 3)
    name = config.get('name', '致盲')
    
    buff_config = {
        'type': 'debuff',
        'name': name,
        'duration': duration,
        'max_stacks': 1,
        'stack_mode': 'refresh',
        'effects': [
            {'type': 'stat_mod', 'stat': 'accuracy', 'value': debuff_value}
        ],
        'trigger_on': 'turn_start',
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_blind',
        'value': debuff_value,
    }

@register_effect("apply_curse")
def apply_curse_effect(config, attacker, target, context):
    """
    诅咒：受到的所有伤害增加
    
    Config:
        damage_increase: 伤害增幅（0.3 = +30%）
        duration: 持续回合数
    """
    damage_increase = config.get('damage_increase', 0.3)
    duration = config.get('duration', 3)
    name = config.get('name', '诅咒')
    
    buff_config = {
        'type': 'debuff',
        'name': name,
        'duration': duration,
        'max_stacks': 1,
        'stack_mode': 'refresh',
        'effects': [],
        'trigger_on': 'turn_start',
        'extra': {
            'damage_increase': damage_increase,
        }
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_curse',
        'damage_increase': damage_increase,
    }

@register_effect("apply_qi_drain")
def apply_qi_drain_effect(config, attacker, target, context):
    """
    灵力流失：每回合损失灵力
    
    Config:
        tick_drain: 每回合消耗灵力
        duration: 持续回合数
    """
    tick_drain = config.get('tick_drain', 10)
    duration = config.get('duration', 3)
    name = config.get('name', '灵力流失')
    
    buff_config = {
        'type': 'debuff',
        'name': name,
        'duration': duration,
        'max_stacks': 3,
        'stack_mode': 'add',
        'effects': [
            {'type': 'qi_drain', 'value': tick_drain}
        ],
        'trigger_on': 'turn_start',
        'tick_interval': 1,
        'show_tick_message': True,
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_qi_drain',
        'tick_drain': tick_drain,
    }

# ========================================
# 修仙特色Debuff
# ========================================

@register_effect("apply_burn")
def apply_burn_effect(config, attacker, target, context):
    """
    灼烧：火系持续伤害 + 降低治疗效果
    
    Config:
        tick_damage: 每回合伤害
        heal_reduce: 治疗效果降低（0.3 = 30%）
        duration: 持续回合数
    """
    tick_damage = config.get('tick_damage', 12)
    heal_reduce = config.get('heal_reduce', 0.3)
    duration = config.get('duration', 3)
    name = config.get('name', '灼烧')
    
    buff_config = {
        'type': 'dot',
        'name': name,
        'duration': duration,
        'max_stacks': 5,
        'stack_mode': 'add',
        'effects': [
            {'type': 'damage', 'value': tick_damage, 'element': 'fire'}
        ],
        'trigger_on': 'turn_start',
        'tick_interval': 1,
        'show_tick_message': True,
        'extra': {
            'heal_reduce': heal_reduce,
        }
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_burn',
        'tick_damage': tick_damage,
    }

@register_effect("apply_frozen")
def apply_frozen_effect(config, attacker, target, context):
    """
    冰封：水系持续伤害 + 降低速度
    
    Config:
        tick_damage: 每回合伤害
        slow_value: 速度减少量
        duration: 持续回合数
    """
    tick_damage = config.get('tick_damage', 8)
    slow_value = config.get('slow_value', -10)
    duration = config.get('duration', 3)
    name = config.get('name', '冰封')
    
    buff_config = {
        'type': 'dot',
        'name': name,
        'duration': duration,
        'max_stacks': 3,
        'stack_mode': 'add',
        'effects': [
            {'type': 'damage', 'value': tick_damage, 'element': 'water'},
            {'type': 'stat_mod', 'stat': 'agility', 'value': slow_value}
        ],
        'trigger_on': 'turn_start',
        'tick_interval': 1,
        'show_tick_message': True,
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_frozen',
        'tick_damage': tick_damage,
    }

@register_effect("apply_shock")
def apply_shock_effect(config, attacker, target, context):
    """
    雷击麻痹：雷系持续伤害 + 有概率晕眩
    
    Config:
        tick_damage: 每回合伤害
        stun_chance: 晕眩概率
        duration: 持续回合数
    """
    tick_damage = config.get('tick_damage', 10)
    stun_chance = config.get('stun_chance', 0.2)
    duration = config.get('duration', 3)
    name = config.get('name', '雷击麻痹')
    
    buff_config = {
        'type': 'dot',
        'name': name,
        'duration': duration,
        'max_stacks': 3,
        'stack_mode': 'add',
        'effects': [
            {'type': 'damage', 'value': tick_damage, 'element': 'lightning'}
        ],
        'trigger_on': 'turn_start',
        'tick_interval': 1,
        'show_tick_message': True,
        'extra': {
            'stun_chance': stun_chance,
        }
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_shock',
        'tick_damage': tick_damage,
    }

@register_effect("apply_corrosion")
def apply_corrosion_effect(config, attacker, target, context):
    """
    腐蚀：毒系持续伤害 + 降低防御
    
    Config:
        tick_damage: 每回合伤害
        defense_reduce: 防御减少量
        duration: 持续回合数
    """
    tick_damage = config.get('tick_damage', 10)
    defense_reduce = config.get('defense_reduce', -5)
    duration = config.get('duration', 3)
    name = config.get('name', '腐蚀')
    
    buff_config = {
        'type': 'dot',
        'name': name,
        'duration': duration,
        'max_stacks': 5,
        'stack_mode': 'add',
        'effects': [
            {'type': 'damage', 'value': tick_damage, 'element': 'poison'},
            {'type': 'stat_mod', 'stat': 'defense', 'value': defense_reduce}
        ],
        'trigger_on': 'turn_start',
        'tick_interval': 1,
        'show_tick_message': True,
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_corrosion',
        'tick_damage': tick_damage,
    }

@register_effect("qi_drain")
def qi_drain_effect(config, attacker, target, context):
    """
    灵力消耗效果（内部使用）
    
    Config:
        value: 消耗灵力值
    """
    drain_value = config.get('value', 10)
    
    old_qi = target.ndb.qi
    target.ndb.qi = max(0, target.ndb.qi - drain_value)
    actual_drain = old_qi - target.ndb.qi
    
    return {
        'type': 'qi_drain',
        'value': actual_drain,
    }
