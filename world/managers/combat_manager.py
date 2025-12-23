"""
战斗管理器 - 存档修复版
修改点:
1. 战斗结束时保存 HP/Qi 到 db
2. 支持事件触发存档
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
            'current_turn': 0,
            'delayed_call': delayed_call
        }
        
        attacker.msg(f"|r【战斗开始】|n")
        target.msg(f"|r【战斗开始】|n")
        
        logger.log_info(f"[战斗] {attacker.key} vs {target.key} 开始")
        
        return True
    
    def _combat_tick(self, combat_id):
        """战斗Tick"""
        combat_data = self.active_combats.get(combat_id)
        if not combat_data:
            return
        
        attacker = combat_data['attacker']
        target = combat_data['target']
        current_turn = combat_data['current_turn']
        
        if not attacker or not target:
            self._end_combat(combat_id, None)
            return
        
        # 根据回合决定谁攻击
        if current_turn == 0:
            actor = attacker
            defender = target
        else:
            actor = target
            defender = attacker
        
        # 检查HP
        actor_hp = getattr(actor.ndb, 'hp', None)
        defender_hp = getattr(defender.ndb, 'hp', None)
        
        if actor_hp is None or defender_hp is None:
            actor.msg("|r错误：角色属性未初始化！|n")
            self._end_combat(combat_id, None)
            return
        
        if defender_hp <= 0:
            winner = attacker if current_turn == 0 else target
            self._end_combat(combat_id, winner)
            return
        
        if actor_hp <= 0:
            winner = target if current_turn == 0 else attacker
            self._end_combat(combat_id, winner)
            return
        
        # 减少冷却
        self.combat_system._reduce_cooldowns(actor)
        
        # 选择技能
        active_skills = actor.get_active_skills()
        
        available = []
        for sk, lv in active_skills:
            cooldown = actor.ndb.skill_cooldowns.get(sk, 0)
            if cooldown <= 0:
                available.append((sk, lv))
        
        if available:
            skill_key, skill_level = self.combat_system._choose_skill_weighted(available)
        else:
            skill_key = 'basic_attack'
            skill_level = actor.db.learned_skills.get('basic_attack', 1)
        
        # 执行攻击
        self.combat_system.use_skill(
            actor,
            defender,
            skill_key,
            skill_level=skill_level,
            callback=lambda result: self._on_turn_complete(combat_id, result)
        )
    
    def _on_turn_complete(self, combat_id, result):
        """单个回合完成"""
        combat_data = self.active_combats.get(combat_id)
        if not combat_data:
            return
        
        attacker = combat_data['attacker']
        target = combat_data['target']
        
        # Buff 处理
        from world.systems.buff_manager import BuffManager
        BuffManager.tick_buffs(attacker, 'turn_end')
        BuffManager.tick_buffs(target, 'turn_end')
        
        # 显示状态
        self._show_combat_status(attacker, target)
        
        # 检查死亡
        attacker_hp = getattr(attacker.ndb, 'hp', 0) or 0
        target_hp = getattr(target.ndb, 'hp', 0) or 0
        
        if target_hp <= 0:
            self._end_combat(combat_id, attacker)
            return
        
        if attacker_hp <= 0:
            self._end_combat(combat_id, target)
            return
        
        # 减少Buff持续时间
        BuffManager.reduce_duration(attacker)
        BuffManager.reduce_duration(target)
        
        # 检查最大回合数
        attacker.ndb.combat_round = getattr(attacker.ndb, 'combat_round', 0) + 1
        if attacker.ndb.combat_round >= self.combat_system.max_rounds:
            attacker.msg("战斗超时！")
            self._end_combat(combat_id, None)
            return
        
        # 切换回合
        combat_data['current_turn'] = 1 - combat_data['current_turn']
        
        # 继续下一个Tick
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
        
        attacker_name = attacker.name or attacker.key
        target_name = target.name or target.key
        
        status_msg = f"\n|w你: HP {attacker_hp}/{attacker_max_hp} | QI {attacker_qi}/{attacker_max_qi}|n"
        status_msg += f"\n|y{target_name}: HP {target_hp}/{target_max_hp}|n\n"
        
        attacker.msg(status_msg)
        
        if hasattr(target, 'msg'):
            target_status = f"\n|w你: HP {target_hp}/{target_max_hp}|n"
            target_status += f"\n|y{attacker_name}: HP {attacker_hp}/{attacker_max_hp}|n\n"
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
        """
        结束战斗
        
        🔥 新增: 战斗结束时同步 ndb → db
        """
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
            
            # NPC死亡变尸体
            if hasattr(loser, 'is_npc') and loser.is_npc:
                self._turn_to_corpse(loser)
            
            rewards = self.combat_system.calculate_combat_rewards(winner, loser)
            
            winner.msg(f"\n|g【胜利！】|n")
            winner.msg(f"获得经验: {rewards['exp']}")
            winner.msg(f"获得金币: {rewards['gold']}")
            
            loser.msg(f"\n|r【战败】|n")
        else:
            attacker.msg("|y【战斗已结束】|n")
            target.msg("|y【战斗已结束】|n")
        
        # 🔥 战斗结束: 同步 HP/Qi 到数据库
        self._save_combat_data(attacker)
        self._save_combat_data(target)
        
        # 🔥 检查是否需要触发存档
        from world.systems.save_system import SaveSystem
        if SaveSystem.should_save_on_event('combat_end'):
            if hasattr(attacker, 'account'):  # 玩家角色
                SaveSystem.save_character(attacker)
            if hasattr(target, 'account'):
                SaveSystem.save_character(target)
        
        logger.log_info(f"[战斗] {attacker.key} vs {target.key} 结束")
    
    def _save_combat_data(self, character):
        """
        🔥 新增: 保存战斗数据到数据库
        
        只保存 HP/Qi,其他属性不动
        注意: 不保存装备加成,直接存 ndb 的值
        """
        if not hasattr(character, 'attributes'):
            return
        
        # 保存当前 HP/Qi (战斗后的实际值)
        current_hp = getattr(character.ndb, 'hp', None)
        current_qi = getattr(character.ndb, 'qi', None)
        
        if current_hp is not None:
            character.attributes.add('hp', current_hp)
        
        if current_qi is not None:
            character.attributes.add('qi', current_qi)
        
        # 🔥 重要: 战斗后血量可能变化,需要封顶检查
        max_hp = getattr(character.ndb, 'max_hp', 100)
        if current_hp and current_hp > max_hp:
            character.attributes.add('hp', max_hp)
    
    def _turn_to_corpse(self, npc):
        """NPC变成尸体"""
        npc.db.original_name = npc.name
        npc.db.original_desc = npc.desc
        
        npc.name = f"{npc.db.original_name}的尸体"
        npc.desc = f"{npc.db.original_desc}\n\n|r尸体已经冰冷，散发着淡淡的血腥味。|n"
        npc.db.is_corpse = True
        
        if npc.location:
            npc.location.msg_contents(f"|r{npc.db.original_name}倒地身亡！|n")
        
        respawn_time = npc.db.respawn_time or 300
        reactor.callLater(respawn_time, self._respawn_npc, npc)
        
        logger.log_info(f"[战斗] {npc.db.original_name} 死亡，{respawn_time}秒后重生")
    
    def _respawn_npc(self, npc):
        """NPC重生"""
        if npc.location:
            npc.location.msg_contents("|w一阵青烟散去...|n")
        
        npc.name = npc.db.original_name
        npc.desc = npc.db.original_desc
        del npc.db.is_corpse
        del npc.db.original_name
        del npc.db.original_desc
        
        if hasattr(npc, '_init_ndb_attributes'):
            npc._init_ndb_attributes()
        
        if npc.location:
            npc.location.msg_contents(f"|g{npc.name}重新出现了！|n")
        
        logger.log_info(f"[战斗] {npc.name} 重生")

COMBAT_MANAGER = CombatManager()