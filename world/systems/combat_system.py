#/home/gg/xx/xxx/world/systems/combat_system.py
"""
战斗系统核心 - 最终核验完整版
支持：反击判定、100%命中反击、轮流回合制
修复：
1. 彻底解决瞬发攻击（普攻/反击）显示“造成0点伤害”的竞态问题
2. 保持战斗文本的时间轴连贯性
3. 包含完整的技能权重选择逻辑(_choose_skill_weighted)
4. 包含冷却减少逻辑(_reduce_cooldowns)
"""
import random
from twisted.internet import reactor
from evennia.utils import logger
from world.loaders.game_data import GAME_DATA, get_config, get_data
from world.systems.skill_effects import apply_effect
from world.systems.quest_system import QUEST_SYSTEM

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
    
    def use_skill(self, attacker, target, skill_key, skill_level=None, is_counter_attack=False, callback=None):
        """使用技能"""
        # 1. 获取技能数据
        if skill_level is None:
            learned = getattr(attacker.db, 'learned_skills', {}) or {}
            skill_level = learned.get(skill_key, 1)
        
        from world.loaders.skill_loader import get_skill_at_level
        skill_data = get_skill_at_level(skill_key, skill_level)
        
        if not skill_data:
            if callback: callback({'success': False, 'reason': '技能不存在'})
            return
        
        # 2. 检查消耗和冷却
        can_use, reason = self._check_skill_usable(attacker, skill_data, skill_key)
        if not can_use:
            attacker.msg(f"|r{reason}|n")
            if callback: callback({'success': False, 'reason': reason})
            return
        
        # 3. 扣除消耗并设置冷却
        self._consume_skill_cost(attacker, skill_data)
        cooldown = skill_data.get('cooldown', 0)
        if cooldown > 0:
            attacker.ndb.skill_cooldowns[skill_key] = cooldown
            
        # 4. 初始化上下文 (Shared Context)
        # 这里的 total_damage 会在逻辑执行后更新，供文本读取
        context = {
            'attacker': attacker,
            'target': target,
            'skill': skill_data,
            'total_damage': 0,
            'total_heal': 0,
            'reflect_damage': 0,
            'is_critical': False,
            'hit': False,
            'countered': False
        }

        # 获取施法时间
        cast_time = skill_data.get('cast_time', 0)
        
        # 5. 预先判定战斗结果
        trigger_execution = True 
        
        # --- 反击判定 ---
        if not is_counter_attack and self._check_counter_before_hit(attacker, target, skill_data):
            context['countered'] = True
            trigger_execution = False 
            
            # 攻击者播放施法前摇
            cast_texts = skill_data.get('battle_text', {}).get('cast', [])
            
            # 防御者播放反击触发文本
            defender_name = target.name or target.key
            counter_msg = f"|y{defender_name}身形一闪，格挡了攻击并准备反击！|n"
            
            # 调度施法文本
            self._schedule_battle_texts(cast_texts, cast_time, attacker, target, context)
            
            # 施法结束瞬间触发反击逻辑
            reactor.callLater(
                cast_time,
                lambda: self._execute_counter_trigger(target, attacker, counter_msg, callback)
            )
            return

        # --- 命中/暴击判定 ---
        if is_counter_attack:
            hit_result = {'hit': True, 'is_critical': self._check_crit(attacker, skill_data)}
        else:
            hit_result = self._check_hit(attacker, target, skill_data)
        
        context['hit'] = hit_result['hit']
        context['is_critical'] = hit_result.get('is_critical', False)

        # 6. 选择对应的文本组
        if is_counter_attack:
            cast_texts = skill_data.get('battle_text', {}).get('counter_cast', 
                         skill_data.get('battle_text', {}).get('cast', []))
            
            if context['is_critical']:
                result_texts = skill_data.get('battle_text', {}).get('counter_critical',
                               skill_data.get('battle_text', {}).get('critical', []))
            else:
                result_texts = skill_data.get('battle_text', {}).get('counter_hit',
                               skill_data.get('battle_text', {}).get('hit', []))
        else:
            cast_texts = skill_data.get('battle_text', {}).get('cast', [])
            
            if not context['hit']:
                result_texts = skill_data.get('battle_text', {}).get('dodge', [])
            elif context['is_critical']:
                result_texts = skill_data.get('battle_text', {}).get('critical', [])
            else:
                result_texts = skill_data.get('battle_text', {}).get('hit', [])

        # 7. 统一调度所有文本
        max_delay_cast = self._schedule_battle_texts(cast_texts, cast_time, attacker, target, context)
        max_delay_result = self._schedule_battle_texts(result_texts, cast_time, attacker, target, context)
        
        final_delay = max(cast_time, max_delay_cast, max_delay_result)

        # 8. 调度逻辑执行
        if trigger_execution:
            # 核心逻辑：伤害计算安排在 cast_time 执行
            reactor.callLater(
                cast_time,
                self._execute_skill_logic,
                attacker, target, skill_data, context, skill_key, callback, final_delay
            )

    def _execute_skill_logic(self, attacker, target, skill_data, context, skill_key, callback, final_delay):
        """执行技能的数值逻辑（计算伤害、应用效果）"""
        
        if not context['hit']:
            # 闪避情况
            remaining_time = max(0, final_delay - skill_data.get('cast_time', 0))
            reactor.callLater(remaining_time + 0.5, lambda: callback({
                'success': True, 'hit': False, 'countered': False
            }) if callback else None)
            return

        # 应用效果 (context['total_damage'] 在此处被更新)
        for effect_config in skill_data.get('effects', []):
            apply_effect(effect_config, attacker, target, context)
        
        # 计算剩余等待时间 (确保文本显示完成后再回调结束回合)
        wait_time = max(0, final_delay - skill_data.get('cast_time', 0))
        
        reactor.callLater(
            wait_time + 0.5,
            lambda: callback({
                'success': True,
                'hit': True,
                'damage': context.get('total_damage', 0),
                'countered': False
            }) if callback else None
        )

    def _execute_counter_trigger(self, defender, attacker, msg, original_callback):
        """执行反击触发"""
        defender.msg(msg)
        attacker.msg(msg)
        
        # 0.5秒后执行具体的反击技能
        reactor.callLater(
            0.5,
            self._execute_counter,
            defender,
            attacker,
            lambda: original_callback({
                'success': True,
                'countered': True,
                'hit': False
            }) if original_callback else None
        )

    def _schedule_battle_texts(self, battle_texts, base_time, attacker, target, context):
        """
        调度战斗文本
        关键修复：如果是结算阶段(100%或之后)的文本，强制增加微小延迟，
        确保先执行逻辑计算(damage不为0)，再执行文本格式化。
        """
        max_delay = 0
        
        for text_data in battle_texts:
            text_template = text_data.get('text', '')
            delay_percent = text_data.get('delay_percent', 0)
            
            # 计算理论延迟
            delay = base_time * (delay_percent / 100.0)
            
            # === 0伤害修复核心 ===
            # 如果文本计划在施法结束时刻显示（例如瞬发技能的命中描述），
            # 此时逻辑计算也是在 delay(0s) 执行。
            # 为了避免竞态，强制文本延后 0.1s，让逻辑先跑完。
            if delay >= base_time:
                delay += 0.1
                
            max_delay = max(max_delay, delay)
            
            reactor.callLater(
                delay,
                self._send_deferred_message,
                attacker,
                target,
                text_template,
                context
            )
            
        return max_delay

    def _send_deferred_message(self, attacker, target, template, context):
        """延迟发送消息（在发送的一刻才读取 context 中的伤害值）"""
        try:
            fmt_data = {
                'caster': attacker.name or attacker.key,
                'target': target.name or target.key,
                'damage': int(context.get('total_damage', 0)),
                'heal': int(context.get('total_heal', 0)),
                'reflect_damage': int(context.get('reflect_damage', 0)),
            }
            text = template.format(**fmt_data)
            
            attacker.msg(text)
            if hasattr(target, 'msg'):
                target.msg(text)
        except Exception as e:
            logger.log_err(f"[Combat] Message formatting error: {e}")

    # ================= 辅助判定逻辑 =================

    def _check_counter_before_hit(self, attacker, target, skill_data):
        """判定是否触发反击"""
        base_rate = get_config('combat.counter.base_rate', 0.02)
        skill_counter = skill_data.get('counter_chance', 0)
        target_counter = getattr(target.ndb, 'counter_rate', 0) or 0
        
        target_level = getattr(target.ndb, 'level', 1) or 1
        attacker_level = getattr(attacker.ndb, 'level', 1) or 1
        level_bonus = (target_level - attacker_level) * get_config('combat.counter.level_diff_bonus', 0.01)
        
        target_agility = getattr(target.ndb, 'agility', 10) or 10
        agility_bonus = target_agility * get_config('combat.counter.agility_bonus', 0.001)
        
        total_rate = base_rate + skill_counter + target_counter + level_bonus + agility_bonus
        max_rate = get_config('combat.counter.max_rate', 0.50)
        final_rate = min(max(total_rate, 0), max_rate)
        
        return random.random() < final_rate

    def _check_hit(self, attacker, target, skill_data):
        """判定命中和暴击"""
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
            return {'hit': False, 'is_critical': False}
            
        return {'hit': True, 'is_critical': self._check_crit(attacker, skill_data)}

    def _check_crit(self, attacker, skill_data):
        """判定暴击"""
        base_crit = get_config('combat.critical_chance', 0.05)
        skill_crit_bonus = skill_data.get('crit_bonus', 0)
        return random.random() < (base_crit + skill_crit_bonus)

    def _execute_counter(self, defender, attacker, callback):
        """执行反击（100%命中）"""
        counter_result = self._choose_counter_skill(defender)
        
        if isinstance(counter_result, tuple):
            counter_skill_key, counter_skill_level = counter_result
        else:
            counter_skill_key = counter_result
            counter_skill_level = 1
        
        if not counter_skill_key:
            if callback: callback()
            return
        
        # 执行反击技能
        self.use_skill(
            defender, 
            attacker, 
            counter_skill_key,
            skill_level=counter_skill_level,
            is_counter_attack=True,
            callback=lambda result: callback() if callback else None
        )
    
    def _choose_counter_skill(self, character):
        """选择反击技能"""
        active_skills = character.get_active_skills() if hasattr(character, 'get_active_skills') else []
        
        if not active_skills:
            return ('basic_attack', 1)
        
        available = []
        weights = []
        
        for skill_key, skill_level in active_skills:
            # 检查冷却
            if character.ndb.skill_cooldowns.get(skill_key, 0) > 0:
                continue
            
            skill_data = get_data('skills', skill_key)
            if not skill_data:
                continue
            
            weight = skill_data.get('counter_weight', 1)
            available.append((skill_key, skill_level))
            weights.append(weight)
        
        if not available:
            return ('basic_attack', 1)
        
        return random.choices(available, weights=weights, k=1)[0]
    
    def _choose_skill_weighted(self, available_skills):
        """
        按权重选择技能（此方法被 CombatManager 调用）
        """
        if not available_skills:
            return ('basic_attack', 1)
        
        weights = []
        for skill_key, skill_level in available_skills:
            skill_data = get_data('skills', skill_key)
            if skill_data:
                weight = skill_data.get('counter_weight', 1)
            else:
                weight = 1
            weights.append(weight)
        
        chosen = random.choices(available_skills, weights=weights, k=1)[0]
        return chosen
    
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
        """减少技能冷却（此方法被 CombatManager 调用）"""
        if not hasattr(character.ndb, 'skill_cooldowns'):
            character.ndb.skill_cooldowns = {}
        
        for skill_key in list(character.ndb.skill_cooldowns.keys()):
            character.ndb.skill_cooldowns[skill_key] -= 1
            if character.ndb.skill_cooldowns[skill_key] <= 0:
                del character.ndb.skill_cooldowns[skill_key]
    
    def calculate_combat_rewards(self, winner, loser):
        """计算战斗奖励"""
        exp_per_level = get_config('combat.exp_per_enemy_level', 10)
        gold_per_level = get_config('combat.gold_per_enemy_level', 5)
        
        loser_level = getattr(loser.ndb, 'level', 1)
        
        base_exp = exp_per_level * loser_level
        exp_reward = int(base_exp * random.uniform(0.9, 1.1))
        
        base_gold = gold_per_level * loser_level
        gold_reward = int(base_gold * random.uniform(0.8, 1.2))
        
        if hasattr(winner, 'account'):
            QUEST_SYSTEM.on_kill(winner, loser.key)
        
        return {'exp': exp_reward, 'gold': gold_reward, 'items': []}