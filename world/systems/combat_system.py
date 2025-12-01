"""
战斗系统核心 - 修复版
"""
import random
from twisted.internet import reactor
from evennia.utils import logger
from world.loaders.game_data import GAME_DATA, get_config, get_data
from world.systems.skill_effects import apply_effect

class CombatSystem:
    DEBUG_COMBAT = False
    """战斗系统"""
    
    
    def __init__(self):
        self.turn_interval = get_config('combat.turn_interval', 2.0)
        self.max_rounds = get_config('combat.max_combat_rounds', 100)
    
    def start_combat(self, attacker, target):
        """开始战斗"""
        if hasattr(attacker.ndb, 'in_combat') and attacker.ndb.in_combat:
            return False
        if hasattr(target.ndb, 'in_combat') and target.ndb.in_combat:
            return False
        
        attacker.ndb.in_combat = True
        attacker.ndb.combat_target = target
        attacker.ndb.combat_round = 0
        attacker.ndb.skill_cooldowns = {}
        
        target.ndb.in_combat = True
        target.ndb.combat_target = attacker
        target.ndb.combat_round = 0
        target.ndb.skill_cooldowns = {}
        
        #logger.log_info(f"[战斗] {attacker.key} vs {target.key} 开始")
        return True
    
    def end_combat(self, char1, char2, winner=None):
        """结束战斗"""
        for char in [char1, char2]:
            if hasattr(char.ndb, 'in_combat'):
                char.ndb.in_combat = False
            if hasattr(char.ndb, 'combat_target'):
                del char.ndb.combat_target
            if hasattr(char.ndb, 'combat_round'):
                del char.ndb.combat_round
            if hasattr(char.ndb, 'skill_cooldowns'):
                del char.ndb.skill_cooldowns
        
        logger.log_info(f"[战斗] {char1.key} vs {char2.key} 结束")
    
    def use_skill(self, attacker, target, skill_key, callback=None):
        """使用技能"""
        skill_data = get_data('skills', skill_key)
        
        if not skill_data:
            if callback:
                callback({'success': False, 'reason': '技能不存在'})
            return
        
        # 检查消耗和冷却
        can_use, reason = self._check_skill_usable(attacker, skill_data, skill_key)
        if not can_use:
            attacker.msg(f"|r{reason}|n")
            if callback:
                callback({'success': False, 'reason': reason})
            return
        
        # 扣除消耗
        self._consume_skill_cost(attacker, skill_data)
        
        # 设置冷却
        cooldown = skill_data.get('cooldown', 0)
        if cooldown > 0:
            attacker.ndb.skill_cooldowns[skill_key] = cooldown
        
        # 获取施法时间
        cast_time = skill_data.get('cast_time', 0)
        
        # 显示施法描述
        self._show_battle_text(
            skill_data.get('battle_text', {}).get('cast', []),
            cast_time,
            attacker,
            target,
            {}
        )
        
        # 在施法完成后执行效果
        reactor.callLater(
            cast_time,
            self._execute_skill_effects,
            attacker,
            target,
            skill_data,
            skill_key,
            callback
        )
    
    def _execute_skill_effects(self, attacker, target, skill_data, skill_key, callback):
        """执行技能效果"""
        context = {
            'attacker': attacker,
            'target': target,
            'skill': skill_data,
            'total_damage': 0,
            'total_heal': 0,
        }
        
        # 1. 命中判定
        hit_result = self._check_hit(attacker, target, skill_data)
        
        if not hit_result['hit']:
            # 闪避
            battle_texts = skill_data.get('battle_text', {}).get('dodge', [])
            max_delay = self._show_battle_text(battle_texts, 0, attacker, target, context)
            
            # 在所有描述显示完后调用回调
            reactor.callLater(max_delay + 0.5, lambda: callback({'success': True, 'hit': False}) if callback else None)
            return
        
        # 2. 暴击判定
        context['is_critical'] = hit_result.get('is_critical', False)
        
        # 3. 应用效果
        for effect_config in skill_data.get('effects', []):
            result = apply_effect(effect_config, attacker, target, context)
        
        # 4. 反击判定
        counter_triggered = self._check_counter(attacker, target, context)
        
        # 5. 显示战斗描述
        if counter_triggered:
            battle_texts = skill_data.get('battle_text', {}).get('countered', [])
        elif context.get('is_critical'):
            battle_texts = skill_data.get('battle_text', {}).get('critical', [])
        else:
            battle_texts = skill_data.get('battle_text', {}).get('hit', [])
        
        max_delay = self._show_battle_text(battle_texts, 0, attacker, target, context)
        
        # 6. 执行反击
        if counter_triggered:
            reactor.callLater(
                max_delay + 0.5,
                self._execute_counter,
                target,
                attacker,
                lambda: callback({
                    'success': True,
                    'hit': True,
                    'damage': context.get('total_damage', 0),
                    'counter': True
                }) if callback else None
            )
        else:
            # 在所有描述显示完后调用回调
            reactor.callLater(
                max_delay + 0.5,
                lambda: callback({
                    'success': True,
                    'hit': True,
                    'damage': context.get('total_damage', 0),
                    'counter': False
                }) if callback else None
            )
    
    def _check_hit(self, attacker, target, skill_data):
        """命中判定"""
        base_accuracy = skill_data.get('accuracy', 0.9)
        
        accuracy_scale = skill_data.get('accuracy_scale', {})
        attr_bonus = sum([
            (getattr(attacker.ndb, attr, 0) or 0) * ratio
            for attr, ratio in accuracy_scale.items()
        ])
        
        final_accuracy = base_accuracy + attr_bonus
        
        dodge_rate = getattr(target.ndb, 'dodge_rate', 0.1) or 0.1
        
        hit_chance = max(0.05, final_accuracy - dodge_rate)
        hit = random.random() < hit_chance
        
        if not hit:
            return {'hit': False}
        
        crit_chance = get_config('combat.critical_chance', 0.05)
        is_critical = random.random() < crit_chance
        
        return {'hit': True, 'is_critical': is_critical}
    
    def _check_counter(self, attacker, target, context):
        """反击判定"""
        passive_skills = getattr(target.ndb, 'passive_skills', []) or []
        
        for passive_key in passive_skills:
            passive_data = get_data('skills', passive_key)
            
            if not passive_data:
                continue
            
            if passive_data.get('trigger') != 'on_hit':
                continue
            
            chance = passive_data.get('chance', 1.0)
            if random.random() < chance:
                context['counter_passive'] = passive_data
                return True
        
        return False
    
    def _execute_counter(self, defender, attacker, callback):
        """执行反击"""
        counter_skill_name = self._choose_counter_skill(defender)
        
        if not counter_skill_name:
            if callback:
                callback()
            return
        
        # 显示反击触发文本
        passive_skills = getattr(defender.ndb, 'passive_skills', [])
        for passive_key in passive_skills:
            passive_data = get_data('skills', passive_key)
            if passive_data and passive_data.get('trigger') == 'on_hit':
                trigger_text = passive_data.get('battle_text', {}).get('trigger', '')
                if trigger_text:
                    msg = trigger_text.format(
                        caster=defender.key,
                        counter_skill=counter_skill_name
                    )
                    defender.msg(msg)
                    attacker.msg(msg)
                break
        
        # 执行反击技能
        self.use_skill(defender, attacker, counter_skill_name, callback=lambda result: callback() if callback else None)
    
    def _choose_counter_skill(self, character):
        """选择反击技能"""
        skills = getattr(character.ndb, 'skills', None)
        
        if not skills:
            return '普通攻击'
        
        available = []
        for skill_key in skills:
            skill_data = get_data('skills', skill_key)
            if not skill_data:
                continue
            
            if skill_data.get('type') == 'passive':
                continue
            
            cooldown_remaining = character.ndb.skill_cooldowns.get(skill_key, 0)
            if cooldown_remaining > 0:
                continue
            
            available.append(skill_key)
        
        if not available:
            return '普通攻击'
        
        return random.choice(available)
    
    def _show_battle_text(self, battle_texts, base_cast_time, attacker, target, context):
        """
        显示战斗描述
        
        Returns:
            float: 最大延迟时间
        """
        max_delay = 0
        
        for text_data in battle_texts:
            text_template = text_data.get('text', '')
            delay_percent = text_data.get('delay_percent', 0)
            
            delay = base_cast_time * (delay_percent / 100.0)
            max_delay = max(max_delay, delay)
            
            variables = {
                'caster': attacker.key,
                'target': target.key,
                'damage': context.get('total_damage', 0),
                'heal': context.get('total_heal', 0),
                'reflect_damage': context.get('reflect_damage', 0),
            }
            
            text = text_template.format(**variables)
            
            reactor.callLater(
                delay,
                self._send_message,
                attacker,
                target,
                text
            )
        
        return max_delay
    
    def _send_message(self, attacker, target, text):
        """发送消息"""
        try:
            attacker.msg(text)
            if hasattr(target, 'msg'):
                target.msg(text)
        except:
            pass
    
    def _check_skill_usable(self, attacker, skill_data, skill_key):
        """检查技能是否可用"""
        cooldown_remaining = attacker.ndb.skill_cooldowns.get(skill_key, 0)
        if cooldown_remaining > 0:
            return False, f"技能冷却中（剩余{cooldown_remaining}回合）"
        
        cost_qi = skill_data.get('cost_qi', 0)
        if cost_qi > 0 and attacker.ndb.qi < cost_qi:
            return False, f"灵力不足"
        
        cost_hp = skill_data.get('cost_hp', 0)
        if cost_hp > 0 and attacker.ndb.hp <= cost_hp:
            return False, f"生命值不足"
        
        return True, ""
    
    def _consume_skill_cost(self, attacker, skill_data):
        """扣除技能消耗"""
        cost_qi = skill_data.get('cost_qi', 0)
        cost_hp = skill_data.get('cost_hp', 0)
        
        if cost_qi > 0:
            attacker.ndb.qi -= cost_qi
        if cost_hp > 0:
            attacker.ndb.hp = max(1, attacker.ndb.hp - cost_hp)
    
    def _reduce_cooldowns(self, character):
        """减少技能冷却"""
        for skill_key in list(character.ndb.skill_cooldowns.keys()):
            character.ndb.skill_cooldowns[skill_key] -= 1
            if character.ndb.skill_cooldowns[skill_key] <= 0:
                del character.ndb.skill_cooldowns[skill_key]
    
    def _choose_skill_for_round(self, character):
        """为回合选择技能"""
        skills = getattr(character.ndb, 'skills', None)
        
        if not skills:
            return '普通攻击'
        
        available = []
        for skill_key in skills:
            skill_data = get_data('skills', skill_key)
            if not skill_data:
                continue
            
            if skill_data.get('type') == 'passive':
                continue
            
            if character.ndb.skill_cooldowns.get(skill_key, 0) > 0:
                continue
            
            available.append(skill_key)
        
        if not available:
            return '普通攻击'
        
        return random.choice(available)
    
    def calculate_combat_rewards(self, winner, loser):
        """计算战斗奖励"""
        exp_per_level = get_config('combat.exp_per_enemy_level', 10)
        gold_per_level = get_config('combat.gold_per_enemy_level', 5)
        
        loser_level = getattr(loser.ndb, 'level', 1)
        
        base_exp = exp_per_level * loser_level
        exp_reward = int(base_exp * random.uniform(0.9, 1.1))
        
        base_gold = gold_per_level * loser_level
        gold_reward = int(base_gold * random.uniform(0.8, 1.2))
        
        return {'exp': exp_reward, 'gold': gold_reward, 'items': []}
