"""
world/systems/skill_effects/buff_effects.py
增益效果（Buff）- 修仙MUD
"""
from . import register_effect
from world.systems.buff_manager import BuffManager

@register_effect("apply_shield")
def apply_shield_effect(config, attacker, target, context):
    """
    灵气护盾：吸收伤害
    
    Config:
        value: 护盾值
        duration: 持续回合数
        name: 护盾名称（可选）
    """
    shield_value = config.get('value', 50)
    duration = config.get('duration', 3)
    name = config.get('name', '灵气护盾')
    
    buff_config = {
        'type': 'buff',
        'name': name,
        'duration': duration,
        'max_stacks': 1,
        'stack_mode': 'refresh',
        'effects': [],
        'trigger_on': 'turn_start',
        'extra': {
            'shield_value': shield_value,
            'current_shield': shield_value,
        }
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_shield',
        'value': shield_value,
    }

@register_effect("apply_attack_boost")
def apply_attack_boost_effect(config, attacker, target, context):
    """
    攻击增强：提升攻击力
    
    Config:
        value: 攻击力加成
        duration: 持续回合数
        stat: 属性名（strength/intelligence等）
    """
    boost_value = config.get('value', 10)
    duration = config.get('duration', 3)
    stat = config.get('stat', 'strength')
    name = config.get('name', '攻击增强')
    
    buff_config = {
        'type': 'buff',
        'name': name,
        'duration': duration,
        'max_stacks': 3,
        'stack_mode': 'add',
        'effects': [
            {'type': 'stat_mod', 'stat': stat, 'value': boost_value}
        ],
        'trigger_on': 'turn_start',
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_attack_boost',
        'value': boost_value,
    }

@register_effect("apply_defense_boost")
def apply_defense_boost_effect(config, attacker, target, context):
    """
    防御增强：提升防御力
    
    Config:
        value: 防御力加成
        duration: 持续回合数
    """
    boost_value = config.get('value', 10)
    duration = config.get('duration', 3)
    name = config.get('name', '防御增强')
    
    buff_config = {
        'type': 'buff',
        'name': name,
        'duration': duration,
        'max_stacks': 3,
        'stack_mode': 'add',
        'effects': [
            {'type': 'stat_mod', 'stat': 'defense', 'value': boost_value}
        ],
        'trigger_on': 'turn_start',
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_defense_boost',
        'value': boost_value,
    }

@register_effect("apply_speed_boost")
def apply_speed_boost_effect(config, attacker, target, context):
    """
    速度提升：提升敏捷
    
    Config:
        value: 敏捷加成
        duration: 持续回合数
    """
    boost_value = config.get('value', 5)
    duration = config.get('duration', 3)
    name = config.get('name', '速度提升')
    
    buff_config = {
        'type': 'buff',
        'name': name,
        'duration': duration,
        'max_stacks': 3,
        'stack_mode': 'add',
        'effects': [
            {'type': 'stat_mod', 'stat': 'agility', 'value': boost_value}
        ],
        'trigger_on': 'turn_start',
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_speed_boost',
        'value': boost_value,
    }

@register_effect("apply_lifesteal")
def apply_lifesteal_effect(config, attacker, target, context):
    """
    吸血：攻击时按比例回复生命
    
    Config:
        ratio: 吸血比例（0.3 = 30%）
        duration: 持续回合数
    
    注意：吸血效果需要在伤害计算后触发，这里只是添加Buff
    实际吸血逻辑在 blood_effects.py 的 lifesteal_effect 中
    """
    ratio = config.get('ratio', 0.3)
    duration = config.get('duration', 3)
    name = config.get('name', '吸血')
    
    buff_config = {
        'type': 'buff',
        'name': name,
        'duration': duration,
        'max_stacks': 1,
        'stack_mode': 'refresh',
        'effects': [],
        'trigger_on': 'turn_start',
        'extra': {
            'lifesteal_ratio': ratio,
        }
    }
    
    BuffManager.add_buff(attacker, buff_config, attacker, duration)
    
    return {
        'type': 'apply_lifesteal',
        'ratio': ratio,
    }

@register_effect("apply_combo")
def apply_combo_effect(config, attacker, target, context):
    """
    连击：有概率额外攻击
    
    Config:
        chance: 触发概率
        duration: 持续回合数
    """
    chance = config.get('chance', 0.3)
    duration = config.get('duration', 3)
    name = config.get('name', '连击')
    
    buff_config = {
        'type': 'buff',
        'name': name,
        'duration': duration,
        'max_stacks': 1,
        'stack_mode': 'refresh',
        'effects': [],
        'trigger_on': 'turn_start',
        'extra': {
            'combo_chance': chance,
        }
    }
    
    BuffManager.add_buff(attacker, buff_config, attacker, duration)
    
    return {
        'type': 'apply_combo',
        'chance': chance,
    }

@register_effect("apply_crit_boost")
def apply_crit_boost_effect(config, attacker, target, context):
    """
    暴击提升：提升暴击率
    
    Config:
        value: 暴击率加成（0.1 = +10%）
        duration: 持续回合数
    """
    crit_boost = config.get('value', 0.1)
    duration = config.get('duration', 3)
    name = config.get('name', '暴击提升')
    
    buff_config = {
        'type': 'buff',
        'name': name,
        'duration': duration,
        'max_stacks': 3,
        'stack_mode': 'add',
        'effects': [
            {'type': 'stat_mod', 'stat': 'critical_chance', 'value': crit_boost}
        ],
        'trigger_on': 'turn_start',
    }
    
    BuffManager.add_buff(attacker, buff_config, attacker, duration)
    
    return {
        'type': 'apply_crit_boost',
        'value': crit_boost,
    }

@register_effect("apply_evasion")
def apply_evasion_effect(config, attacker, target, context):
    """
    免伤：有概率完全抵挡伤害
    
    Config:
        chance: 免伤概率
        duration: 持续回合数
    """
    evasion_chance = config.get('chance', 0.2)
    duration = config.get('duration', 3)
    name = config.get('name', '免伤')
    
    buff_config = {
        'type': 'buff',
        'name': name,
        'duration': duration,
        'max_stacks': 1,
        'stack_mode': 'refresh',
        'effects': [],
        'trigger_on': 'turn_start',
        'extra': {
            'evasion_chance': evasion_chance,
        }
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_evasion',
        'chance': evasion_chance,
    }

@register_effect("apply_reflect")
def apply_reflect_effect(config, attacker, target, context):
    """
    反伤：将受到伤害的一部分反弹
    
    Config:
        ratio: 反伤比例（0.2 = 20%）
        duration: 持续回合数
    """
    reflect_ratio = config.get('ratio', 0.2)
    duration = config.get('duration', 3)
    name = config.get('name', '反伤')
    
    buff_config = {
        'type': 'buff',
        'name': name,
        'duration': duration,
        'max_stacks': 1,
        'stack_mode': 'refresh',
        'effects': [],
        'trigger_on': 'turn_start',
        'extra': {
            'reflect_ratio': reflect_ratio,
        }
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_reflect',
        'ratio': reflect_ratio,
    }

# ========================================
# 修仙特色Buff
# ========================================

@register_effect("apply_qi_regen")
def apply_qi_regen_effect(config, attacker, target, context):
    """
    灵力回复：每回合恢复灵力
    
    Config:
        value: 每回合恢复量
        duration: 持续回合数
    """
    regen_value = config.get('value', 10)
    duration = config.get('duration', 3)
    name = config.get('name', '灵力回复')
    
    buff_config = {
        'type': 'buff',
        'name': name,
        'duration': duration,
        'max_stacks': 3,
        'stack_mode': 'add',
        'effects': [
            {'type': 'restore_qi', 'value': regen_value}
        ],
        'trigger_on': 'turn_start',
        'tick_interval': 1,
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_qi_regen',
        'value': regen_value,
    }

@register_effect("apply_hp_regen")
def apply_hp_regen_effect(config, attacker, target, context):
    """
    生命回复（HoT）：每回合恢复生命
    
    Config:
        value: 每回合恢复量
        duration: 持续回合数
    """
    regen_value = config.get('value', 15)
    duration = config.get('duration', 3)
    name = config.get('name', '生命回复')
    
    buff_config = {
        'type': 'hot',
        'name': name,
        'duration': duration,
        'max_stacks': 3,
        'stack_mode': 'add',
        'effects': [
            {'type': 'heal', 'value': regen_value, 'target': 'self'}
        ],
        'trigger_on': 'turn_start',
        'tick_interval': 1,
        'show_tick_message': True,
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_hp_regen',
        'value': regen_value,
    }

@register_effect("apply_immortal_body")
def apply_immortal_body_effect(config, attacker, target, context):
    """
    不灭真身：血量不会低于1（触发一次后消失）
    
    Config:
        duration: 持续回合数
    """
    duration = config.get('duration', 5)
    name = config.get('name', '不灭真身')
    
    buff_config = {
        'type': 'buff',
        'name': name,
        'duration': duration,
        'max_stacks': 1,
        'stack_mode': 'replace',
        'effects': [],
        'trigger_on': 'turn_start',
        'extra': {
            'immortal': True,
        }
    }
    
    BuffManager.add_buff(target, buff_config, attacker, duration)
    
    return {
        'type': 'apply_immortal_body',
    }