"""
战斗管理器 - 回合制互打版本
每回合：攻击者攻击 → 目标反击（如果活着）
"""
from twisted.internet import reactor
from evennia.utils import logger
from world.systems.combat_system import CombatSystem

class CombatManager:
    """战斗管理器（单例）"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.combat_system = CombatSystem()
        self.active_combats = {}
        self._initialized = True
        
        logger.log_info("[战斗管理器] 初始化完成")
    
    def start_combat(self, attacker, target):
        """开始战斗"""
        if not self.combat_system.start_combat(attacker, target):
            return False
        
        combat_id = f"{attacker.id}_{target.id}"
        
        delayed_call = reactor.callLater(
            1.0,
            self._combat_tick,
            combat_id
        )
        
        self.active_combats[combat_id] = {
            'attacker': attacker,
            'target': target,
            'delayed_call': delayed_call
        }
        
        attacker.msg(f"|r【战斗开始】|n")
        target.msg(f"|r【战斗开始】|n")
        
        logger.log_info(f"[战斗] {attacker.key} vs {target.key} 开始")
        
        return True
    
    def _combat_tick(self, combat_id):
        """战斗回合Tick"""
        combat_data = self.active_combats.get(combat_id)
        if not combat_data:
            return
        
        attacker = combat_data['attacker']
        target = combat_data['target']
        
        if not attacker or not target:
            self._end_combat(combat_id, None)
            return
        
        # 检查HP
        attacker_hp = getattr(attacker.ndb, 'hp', None)
        target_hp = getattr(target.ndb, 'hp', None)
        
        if attacker_hp is None or target_hp is None:
            attacker.msg("|r错误：角色属性未初始化！|n")
            self._end_combat(combat_id, None)
            return
        
        if target_hp <= 0:
            self._end_combat(combat_id, attacker)
            return
        if attacker_hp <= 0:
            self._end_combat(combat_id, target)
            return
        
        # 显示回合信息
        round_num = getattr(attacker.ndb, 'combat_round', 0) + 1
        attacker.msg(f"\n|w【回合 {round_num}】|n")
        target.msg(f"\n|w【回合 {round_num}】|n")
        
        attacker.ndb.combat_round = round_num
        
        # 减少冷却
        self.combat_system._reduce_cooldowns(attacker)
        self.combat_system._reduce_cooldowns(target)
        
        # 攻击者攻击
        skill_key = self.combat_system._choose_skill_for_round(attacker)
        
        self.combat_system.use_skill(
            attacker,
            target,
            skill_key,
            callback=lambda result: self._on_attacker_skill_complete(combat_id, result)
        )
    
    def _on_attacker_skill_complete(self, combat_id, result):
        """攻击者技能完成回调"""
        combat_data = self.active_combats.get(combat_id)
        if not combat_data:
            return
        
        attacker = combat_data['attacker']
        target = combat_data['target']
        
        # 检查目标是否死亡
        if getattr(target.ndb, 'hp', 0) <= 0:
            self._show_combat_status(attacker, target)
            self._end_combat(combat_id, attacker)
            return
        
        # 检查攻击者是否死亡（可能被反击打死）
        if getattr(attacker.ndb, 'hp', 0) <= 0:
            self._show_combat_status(attacker, target)
            self._end_combat(combat_id, target)
            return
        
        # 如果有反击，等反击完成后才执行目标回合
        if result.get('counter'):
            # 反击已经在技能系统中处理了，这里直接继续
            pass
        
        # 目标反击（回合制攻击，不是被动反击）
        target_skill = self.combat_system._choose_skill_for_round(target)
        
        self.combat_system.use_skill(
            target,
            attacker,
            target_skill,
            callback=lambda r: self._on_target_skill_complete(combat_id, r)
        )
    
    def _on_target_skill_complete(self, combat_id, result):
        """目标反击完成回调"""
        combat_data = self.active_combats.get(combat_id)
        if not combat_data:
            return
        
        attacker = combat_data['attacker']
        target = combat_data['target']
        
        # 显示状态
        self._show_combat_status(attacker, target)
        
        # 检查是否死亡
        if getattr(target.ndb, 'hp', 0) <= 0:
            self._end_combat(combat_id, attacker)
            return
        
        if getattr(attacker.ndb, 'hp', 0) <= 0:
            self._end_combat(combat_id, target)
            return
        
        # 检查最大回合数
        if attacker.ndb.combat_round >= self.combat_system.max_rounds:
            attacker.msg("战斗超时！")
            self._end_combat(combat_id, None)
            return
        
        # 继续下一回合
        delayed_call = reactor.callLater(
            self.combat_system.turn_interval,
            self._combat_tick,
            combat_id
        )
        combat_data['delayed_call'] = delayed_call
    
    def _show_combat_status(self, attacker, target):
        """显示战斗状态"""
        attacker_hp = getattr(attacker.ndb, 'hp', 0) or 0
        attacker_max_hp = getattr(attacker.ndb, 'max_hp', 1) or 1
        attacker_qi = getattr(attacker.ndb, 'qi', 0) or 0
        attacker_max_qi = getattr(attacker.ndb, 'max_qi', 1) or 1
        
        target_hp = getattr(target.ndb, 'hp', 0) or 0
        target_max_hp = getattr(target.ndb, 'max_hp', 1) or 1
        
        status_msg = f"\n|w你: HP {attacker_hp}/{attacker_max_hp} | QI {attacker_qi}/{attacker_max_qi}|n"
        status_msg += f"\n|y{target.key}: HP {target_hp}/{target_max_hp}|n\n"
        
        attacker.msg(status_msg)
        
        if hasattr(target, 'msg'):
            target_status = f"\n|w你: HP {target_hp}/{target_max_hp}|n"
            target_status += f"\n|y{attacker.key}: HP {attacker_hp}/{attacker_max_hp}|n\n"
            target.msg(target_status)
    
    def stop_combat(self, character):
        """手动停止战斗"""
        for combat_id, combat_data in list(self.active_combats.items()):
            if character in [combat_data['attacker'], combat_data['target']]:
                if combat_data['delayed_call'].active():
                    combat_data['delayed_call'].cancel()
                
                self._end_combat(combat_id, None)
                character.msg("战斗已停止")
                return True
        
        return False
    
    def _end_combat(self, combat_id, winner):
        """结束战斗"""
        combat_data = self.active_combats.get(combat_id)
        if not combat_data:
            return
        
        attacker = combat_data['attacker']
        target = combat_data['target']
        
        if combat_data['delayed_call'].active():
            combat_data['delayed_call'].cancel()
        
        self.combat_system.end_combat(attacker, target, winner)
        
        del self.active_combats[combat_id]
        
        if winner:
            loser = target if winner == attacker else attacker
            
            rewards = self.combat_system.calculate_combat_rewards(winner, loser)
            
            winner.msg(f"\n|g【胜利！】|n")
            winner.msg(f"获得经验: {rewards['exp']}")
            winner.msg(f"获得金币: {rewards['gold']}")
            
            loser.msg(f"\n|r【战败】|n")
        else:
            attacker.msg("|y【战斗已结束】|n")
            target.msg("|y【战斗已结束】|n")
        
        logger.log_info(f"[战斗] {attacker.key} vs {target.key} 结束")

COMBAT_MANAGER = CombatManager()
