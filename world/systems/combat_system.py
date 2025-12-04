"""
战斗系统核心 - 修复版
支持：反击判定、100%命中反击、轮流回合制
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
        """使用技能
        
        Args:
            attacker: 攻击者
            target: 目标
            skill_key: 技能key
            skill_level (int): 技能等级（None则从角色读取）
            is_counter_attack (bool): 是否为反击攻击（反击100%命中，不触发反击链）
            callback: 回调函数
        """
        # ========== 新增：支持等级系统 ==========
        if skill_level is None:
            # 从角色的learned_skills读取等级
            learned = getattr(attacker.db, 'learned_skills', {}) or {}
            skill_level = learned.get(skill_key, 1)
        
        # 获取指定等级的技能配置
        from world.loaders.skill_loader import get_skill_at_level
        skill_data = get_skill_at_level(skill_key, skill_level)
        
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
        
        # ========== 修改：反击时优先使用 counter_cast 文本 ==========
        if is_counter_attack:
            cast_texts = skill_data.get('battle_text', {}).get('counter_cast', 
                         skill_data.get('battle_text', {}).get('cast', []))
        else:
            cast_texts = skill_data.get('battle_text', {}).get('cast', [])
        
        # 显示施法描述
        self._show_battle_text(cast_texts, cast_time, attacker, target, {})
        
        # 在施法完成后执行效果
        reactor.callLater(
            cast_time,
            self._execute_skill_effects,
            attacker,
            target,
            skill_data,
            skill_key,
            is_counter_attack,
            callback
        )
    
    def _execute_skill_effects(self, attacker, target, skill_data, skill_key, is_counter_attack, callback):
        """执行技能效果"""
        context = {
            'attacker': attacker,
            'target': target,
            'skill': skill_data,
            'total_damage': 0,
            'total_heal': 0,
        }
        
        # ========== 新增：反击判定（在命中判定之前） ==========
        # 反击攻击不触发反击链
        if not is_counter_attack:
            if self._check_counter_before_hit(attacker, target, skill_data):
                # 反击成功 → 目标不受伤 + 反击攻击
                # 显示统一的反击触发文本
                defender_name = target.name or target.key
                counter_msg = f"|y{defender_name}身形一闪，格挡了攻击！|n"
                attacker.msg(counter_msg)
                target.msg(counter_msg)
                
                reactor.callLater(
                    0.5,
                    self._execute_counter,
                    target,
                    attacker,
                    lambda: callback({
                        'success': True,
                        'countered': True,
                        'hit': False
                    }) if callback else None
                )
                return  # 直接返回，不继续执行后面的伤害
        
        # ========== 命中判定 ==========
        # 反击攻击100%命中
        if is_counter_attack:
            hit_result = {'hit': True, 'is_critical': False}
        else:
            hit_result = self._check_hit(attacker, target, skill_data)
        
        if not hit_result['hit']:
            # 闪避
            battle_texts = skill_data.get('battle_text', {}).get('dodge', [])
            max_delay = self._show_battle_text(battle_texts, 0, attacker, target, context)
            
            reactor.callLater(
                max_delay + 0.5, 
                lambda: callback({
                    'success': True, 
                    'hit': False,
                    'countered': False
                }) if callback else None
            )
            return
        
        # 暴击判定
        context['is_critical'] = hit_result.get('is_critical', False)
        
        # 应用效果
        for effect_config in skill_data.get('effects', []):
            result = apply_effect(effect_config, attacker, target, context)
        
        # ========== 修改：反击时优先使用 counter_hit 文本 ==========
        if is_counter_attack:
            if context.get('is_critical'):
                battle_texts = skill_data.get('battle_text', {}).get('counter_critical',
                              skill_data.get('battle_text', {}).get('critical', []))
            else:
                battle_texts = skill_data.get('battle_text', {}).get('counter_hit',
                              skill_data.get('battle_text', {}).get('hit', []))
        else:
            # 正常攻击
            if context.get('is_critical'):
                battle_texts = skill_data.get('battle_text', {}).get('critical', [])
            else:
                battle_texts = skill_data.get('battle_text', {}).get('hit', [])
        
        max_delay = self._show_battle_text(battle_texts, 0, attacker, target, context)
        
        # 在所有描述显示完后调用回调
        reactor.callLater(
            max_delay + 0.5,
            lambda: callback({
                'success': True,
                'hit': True,
                'damage': context.get('total_damage', 0),
                'countered': False
            }) if callback else None
        )
    
    def _check_counter_before_hit(self, attacker, target, skill_data):
        """
        在命中判定前，先判断是否反击
        
        Returns:
            bool: True=反击成功（目标不受伤+反击）, False=进入正常命中判定
        """
        # 1. 基础反击率
        base_rate = get_config('combat.counter.base_rate', 0.02)
        
        # 2. 技能配置的反击率
        skill_counter = skill_data.get('counter_chance', 0)
        
        # 3. 目标的反击率属性（装备+被动技能）
        target_counter = getattr(target.ndb, 'counter_rate', 0) or 0
        
        # 4. 等级压制
        target_level = getattr(target.ndb, 'level', 1) or 1
        attacker_level = getattr(attacker.ndb, 'level', 1) or 1
        level_diff = target_level - attacker_level
        level_bonus = level_diff * get_config('combat.counter.level_diff_bonus', 0.01)
        
        # 5. 敏捷加成
        target_agility = getattr(target.ndb, 'agility', 10) or 10
        agility_bonus = target_agility * get_config('combat.counter.agility_bonus', 0.001)
        
        # 6. 总反击率
        total_rate = base_rate + skill_counter + target_counter + level_bonus + agility_bonus
        max_rate = get_config('combat.counter.max_rate', 0.50)
        final_rate = min(max(total_rate, 0), max_rate)
        
        # 7. 判定
        return random.random() < final_rate
    
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
    
    def _execute_counter(self, defender, attacker, callback):
        """执行反击（100%命中）"""
        counter_result = self._choose_counter_skill(defender)
        
        # ========== 新系统：返回(skill_key, skill_level) ==========
        if isinstance(counter_result, tuple):
            counter_skill_key, counter_skill_level = counter_result
        else:
            # 兼容旧代码
            counter_skill_key = counter_result
            counter_skill_level = 1
        
        if not counter_skill_key:
            if callback:
                callback()
            return
        
        # 显示反击触发文本
        defender_name = defender.name or defender.key
        attacker_name = attacker.name or attacker.key
        
        counter_msg = f"|y{defender_name}趁机反击！|n"
        defender.msg(counter_msg)
        attacker.msg(counter_msg)
        
        # 执行反击技能（100%命中）
        self.use_skill(
            defender, 
            attacker, 
            counter_skill_key,
            skill_level=counter_skill_level,  # ← 传递等级
            is_counter_attack=True,
            callback=lambda result: callback() if callback else None
        )
    
    def _choose_counter_skill(self, character):
        """
        选择反击技能（支持权重+等级）
        
        Returns:
            tuple: (skill_key, skill_level)
        """
        # ========== 新系统：从装备的技能选择 ==========
        active_skills = character.get_active_skills()  # [(skill_key, level), ...]
        
        if not active_skills:
            return ('basic_attack', 1)
        
        # 收集可用技能及其权重
        available = []
        weights = []
        
        for skill_key, skill_level in active_skills:
            # 检查冷却
            cooldown_remaining = character.ndb.skill_cooldowns.get(skill_key, 0)
            if cooldown_remaining > 0:
                continue
            
            # 获取技能配置（用于读取权重）
            skill_data = get_data('skills', skill_key)
            if not skill_data:
                continue
            
            # 获取反击权重（默认1）
            weight = skill_data.get('counter_weight', 1)
            
            available.append((skill_key, skill_level))
            weights.append(weight)
        
        if not available:
            return ('basic_attack', 1)
        
        # 按权重随机选择
        import random
        chosen = random.choices(available, weights=weights, k=1)[0]
        return chosen
    
    def _choose_skill_weighted(self, available_skills):
        """
        按权重选择技能（用于战斗回合）
        
        Args:
            available_skills: [(skill_key, level), ...]
        
        Returns:
            tuple: (skill_key, skill_level)
        """
        if not available_skills:
            return ('basic_attack', 1)
        
        weights = []
        for skill_key, skill_level in available_skills:
            skill_data = get_data('skills', skill_key)
            if skill_data:
                # 可以自定义权重字段，这里用counter_weight通用
                weight = skill_data.get('counter_weight', 1)
            else:
                weight = 1
            weights.append(weight)
        
        import random
        chosen = random.choices(available_skills, weights=weights, k=1)[0]
        return chosen
    
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
            
            # 使用中文名显示
            variables = {
                'caster': attacker.name or attacker.key,
                'target': target.name or target.key,
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
        if not hasattr(character.ndb, 'skill_cooldowns'):
            character.ndb.skill_cooldowns = {}
        
        for skill_key in list(character.ndb.skill_cooldowns.keys()):
            character.ndb.skill_cooldowns[skill_key] -= 1
            if character.ndb.skill_cooldowns[skill_key] <= 0:
                del character.ndb.skill_cooldowns[skill_key]
    
    # ========== 删除：旧的技能选择方法 ==========
    # _choose_skill_for_round() 已被新系统替代，不再需要
    
    def calculate_combat_rewards(self, winner, loser):
        """计算战斗奖励"""
        exp_per_level = get_config('combat.exp_per_enemy_level', 10)
        gold_per_level = get_config('combat.gold_per_enemy_level', 5)
        
        loser_level = getattr(loser.ndb, 'level', 1)
        
        base_exp = exp_per_level * loser_level
        exp_reward = int(base_exp * random.uniform(0.9, 1.1))
        
        base_gold = gold_per_level * loser_level
        gold_reward = int(base_gold * random.uniform(0.8, 1.2))
        
        # 通知任务系统击杀事件
        if hasattr(winner, 'account'):  # 确保是玩家
            QUEST_SYSTEM.on_kill(winner, loser.key)
        
        return {'exp': exp_reward, 'gold': gold_reward, 'items': []}