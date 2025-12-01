"""
任务系统核心
"""
from world.loaders.game_data import GAME_DATA
from world.systems.quest_objectives import get_objective_handler
from evennia.utils import logger
import datetime

class QuestSystem:
    """任务系统"""
    
    def __init__(self):
        pass
    
    def can_accept_quest(self, character, quest_id):
        """
        检查是否可以接取任务
        
        Returns:
            tuple: (bool, str) - (是否可接, 原因)
        """
        quest_data = GAME_DATA['quests'].get(quest_id)
        
        if not quest_data:
            return False, "任务不存在"
        
        # 检查是否已接取
        active_quests = character.db.quests.get('active', [])
        if any(q['quest_id'] == quest_id for q in active_quests):
            return False, "已接取该任务"
        
        # 检查是否已完成（非重复任务）
        if not quest_data.get('repeatable', False):
            completed = character.db.quests.get('completed', [])
            if quest_id in completed:
                return False, "已完成该任务"
        
        # 检查每日任务
        if quest_data.get('daily', False):
            today = datetime.date.today().isoformat()
            daily_completed = character.db.quests.get('daily_completed', {})
            if quest_id in daily_completed.get(today, []):
                return False, "今日已完成该任务"
        
        # 检查等级要求
        requirements = quest_data.get('requirements', {})
        
        level_min = requirements.get('level_min')
        if level_min and character.ndb.level < level_min:
            return False, f"等级不足（需要{level_min}级）"
        
        level_max = requirements.get('level_max')
        if level_max and character.ndb.level > level_max:
            return False, f"等级过高（最高{level_max}级）"
        
        # 检查境界要求
        required_realm = requirements.get('realm')
        if required_realm and character.ndb.realm != required_realm:
            return False, f"境界不符（需要{required_realm}）"
        
        # 检查前置任务
        completed_quests = character.db.quests.get('completed', [])
        for prereq in requirements.get('completed_quests', []):
            if prereq not in completed_quests:
                prereq_name = GAME_DATA['quests'].get(prereq, {}).get('name', prereq)
                return False, f"需要先完成：{prereq_name}"
        
        # 检查互斥任务
        for conflict in requirements.get('not_completed_quests', []):
            if conflict in completed_quests:
                return False, "与已完成的任务冲突"
        
        return True, ""
    
    def accept_quest(self, character, quest_id):
        """
        接取任务
        
        Returns:
            bool: 是否成功
        """
        can_accept, reason = self.can_accept_quest(character, quest_id)
        
        if not can_accept:
            return False, reason
        
        quest_data = GAME_DATA['quests'].get(quest_id)
        
        # 初始化任务数据
        if not hasattr(character.db, 'quests') or character.db.quests is None:
            character.db.quests = {
                'active': [],
                'completed': [],
                'failed': [],
                'daily_completed': {}
            }
        
        # 创建任务实例
        quest_instance = {
            'quest_id': quest_id,
            'objectives': [obj.copy() for obj in quest_data.get('objectives', [])],
            'started_at': datetime.datetime.now().isoformat()
        }
        
        character.db.quests['active'].append(quest_instance)
        
        logger.log_info(f"[任务] {character.key} 接取任务: {quest_data.get('name')}")
        
        return True, quest_data.get('name')
    
    def abandon_quest(self, character, quest_id):
        """放弃任务"""
        active_quests = character.db.quests.get('active', [])
        
        for i, quest in enumerate(active_quests):
            if quest['quest_id'] == quest_id:
                quest_data = GAME_DATA['quests'].get(quest_id)
                quest_name = quest_data.get('name', quest_id) if quest_data else quest_id
                
                active_quests.pop(i)
                
                logger.log_info(f"[任务] {character.key} 放弃任务: {quest_name}")
                
                return True, quest_name
        
        return False, "未接取该任务"
    
    def on_kill(self, character, target_name, skill_used=None):
        """
        击杀事件处理
        
        Args:
            character: 玩家
            target_name: 击杀目标名称
            skill_used: 使用的技能
        """
        if not hasattr(character.db, 'quests'):
            return
        
        active_quests = character.db.quests.get('active', [])
        
        for quest_instance in active_quests:
            quest_id = quest_instance['quest_id']
            quest_data = GAME_DATA['quests'].get(quest_id)
            
            if not quest_data:
                continue
            
            # 检查每个目标
            for objective in quest_instance['objectives']:
                if objective.get('type') != 'kill':
                    continue
                
                handler = get_objective_handler('kill')
                if not handler:
                    continue
                
                # 更新进度
                event_data = {
                    'target': target_name,
                    'skill': skill_used
                }
                
                if handler.check_progress(character, objective, event_data):
                    # 通知玩家
                    progress_text = handler.get_progress_text(objective)
                    character.msg(f"|y[任务更新]|n {quest_data.get('name')}: {progress_text}")
                    
                    # 检查任务是否完成
                    if self._check_quest_complete(quest_instance, quest_data):
                        self._notify_quest_complete(character, quest_data)
    
    def on_collect(self, character, item_name, count=1):
        """收集物品事件"""
        if not hasattr(character.db, 'quests'):
            return
        
        active_quests = character.db.quests.get('active', [])
        
        for quest_instance in active_quests:
            quest_id = quest_instance['quest_id']
            quest_data = GAME_DATA['quests'].get(quest_id)
            
            if not quest_data:
                continue
            
            for objective in quest_instance['objectives']:
                if objective.get('type') != 'collect':
                    continue
                
                handler = get_objective_handler('collect')
                if not handler:
                    continue
                
                event_data = {
                    'item': item_name,
                    'count': count
                }
                
                if handler.check_progress(character, objective, event_data):
                    progress_text = handler.get_progress_text(objective)
                    character.msg(f"|y[任务更新]|n {quest_data.get('name')}: {progress_text}")
                    
                    if self._check_quest_complete(quest_instance, quest_data):
                        self._notify_quest_complete(character, quest_data)
    
    def on_talk(self, character, npc_name):
        """对话事件"""
        if not hasattr(character.db, 'quests'):
            return
        
        active_quests = character.db.quests.get('active', [])
        
        for quest_instance in active_quests:
            quest_id = quest_instance['quest_id']
            quest_data = GAME_DATA['quests'].get(quest_id)
            
            if not quest_data:
                continue
            
            for objective in quest_instance['objectives']:
                if objective.get('type') != 'talk':
                    continue
                
                handler = get_objective_handler('talk')
                if not handler:
                    continue
                
                event_data = {'npc': npc_name}
                
                if handler.check_progress(character, objective, event_data):
                    progress_text = handler.get_progress_text(objective)
                    character.msg(f"|y[任务更新]|n {quest_data.get('name')}: {progress_text}")
                    
                    if self._check_quest_complete(quest_instance, quest_data):
                        self._notify_quest_complete(character, quest_data)
    
    def on_explore(self, character, location_key):
        """探索事件"""
        if not hasattr(character.db, 'quests'):
            return
        
        active_quests = character.db.quests.get('active', [])
        
        for quest_instance in active_quests:
            quest_id = quest_instance['quest_id']
            quest_data = GAME_DATA['quests'].get(quest_id)
            
            if not quest_data:
                continue
            
            for objective in quest_instance['objectives']:
                if objective.get('type') != 'explore':
                    continue
                
                handler = get_objective_handler('explore')
                if not handler:
                    continue
                
                event_data = {'location': location_key}
                
                if handler.check_progress(character, objective, event_data):
                    progress_text = handler.get_progress_text(objective)
                    character.msg(f"|y[任务更新]|n {quest_data.get('name')}: {progress_text}")
                    
                    if self._check_quest_complete(quest_instance, quest_data):
                        self._notify_quest_complete(character, quest_data)
    
    def on_cultivate(self, character, duration):
        """修炼事件（秒）"""
        if not hasattr(character.db, 'quests'):
            return
        
        active_quests = character.db.quests.get('active', [])
        
        for quest_instance in active_quests:
            quest_id = quest_instance['quest_id']
            quest_data = GAME_DATA['quests'].get(quest_id)
            
            if not quest_data:
                continue
            
            for objective in quest_instance['objectives']:
                if objective.get('type') != 'cultivate':
                    continue
                
                handler = get_objective_handler('cultivate')
                if not handler:
                    continue
                
                event_data = {'duration': duration}
                
                if handler.check_progress(character, objective, event_data):
                    if self._check_quest_complete(quest_instance, quest_data):
                        self._notify_quest_complete(character, quest_data)
    
    def _check_quest_complete(self, quest_instance, quest_data):
        """检查任务是否完成"""
        for objective in quest_instance['objectives']:
            obj_type = objective.get('type')
            handler = get_objective_handler(obj_type)
            
            if not handler:
                continue
            
            if not handler.is_completed(objective):
                return False
        
        return True
    
    def _notify_quest_complete(self, character, quest_data):
        """通知任务可完成"""
        quest_name = quest_data.get('name', '未知任务')
        finisher = quest_data.get('quest_finisher')
        
        if finisher:
            character.msg(f"|g[任务完成]|n {quest_name} - 请找 {finisher} 交任务")
        else:
            # 自动完成
            self.complete_quest(character, quest_data.get('id'))
    
    def complete_quest(self, character, quest_id):
        """
        完成任务
        
        Returns:
            tuple: (bool, str) - (是否成功, 消息)
        """
        # 查找任务
        active_quests = character.db.quests.get('active', [])
        quest_instance = None
        
        for i, quest in enumerate(active_quests):
            if quest['quest_id'] == quest_id:
                quest_instance = quest
                quest_index = i
                break
        
        if not quest_instance:
            return False, "未接取该任务"
        
        quest_data = GAME_DATA['quests'].get(quest_id)
        if not quest_data:
            return False, "任务数据错误"
        
        # 检查是否完成所有目标
        if not self._check_quest_complete(quest_instance, quest_data):
            return False, "任务目标未完成"
        
        # 发放奖励
        self._give_rewards(character, quest_data)
        
        # 移除活跃任务
        active_quests.pop(quest_index)
        
        # 添加到已完成
        if not quest_data.get('daily', False):
            if 'completed' not in character.db.quests:
                character.db.quests['completed'] = []
            character.db.quests['completed'].append(quest_id)
        else:
            # 每日任务记录
            today = datetime.date.today().isoformat()
            if 'daily_completed' not in character.db.quests:
                character.db.quests['daily_completed'] = {}
            if today not in character.db.quests['daily_completed']:
                character.db.quests['daily_completed'][today] = []
            character.db.quests['daily_completed'][today].append(quest_id)
        
        # 检查任务链
        chain_next = quest_data.get('chain_next')
        if chain_next:
            next_quest = GAME_DATA['quests'].get(chain_next)
            if next_quest:
                character.msg(f"|c[新任务]|n {next_quest.get('name')} 已解锁！")
        
        logger.log_info(f"[任务] {character.key} 完成任务: {quest_data.get('name')}")
        
        return True, quest_data.get('name')
    
    def _give_rewards(self, character, quest_data):
        """发放奖励"""
        rewards = quest_data.get('rewards', {})
        
        reward_msg = []
        
        # 经验
        exp = rewards.get('exp', 0)
        if exp > 0:
            # TODO: 实现经验系统
            reward_msg.append(f"经验 +{exp}")
        
        # 金币
        gold = rewards.get('gold', 0)
        if gold > 0:
            # TODO: 实现金币系统
            reward_msg.append(f"金币 +{gold}")
        
        # 物品
        items = rewards.get('items', [])
        for item in items:
            item_name = item.get('name')
            item_count = item.get('count', 1)
            
            # 添加到背包
            if not hasattr(character.ndb, 'inventory') or character.ndb.inventory is None:
                character.ndb.inventory = {}
            
            character.ndb.inventory[item_name] = character.ndb.inventory.get(item_name, 0) + item_count
            reward_msg.append(f"{item_name} x{item_count}")
        
        # 解锁技能
        unlock_skills = rewards.get('unlock_skills', [])
        for skill in unlock_skills:
            if not hasattr(character.ndb, 'skills') or character.ndb.skills is None:
                character.ndb.skills = []
            
            if skill not in character.ndb.skills:
                character.ndb.skills.append(skill)
                reward_msg.append(f"学会技能: {skill}")
        
        # 显示奖励
        if reward_msg:
            character.msg("|g[任务奖励]|n " + ", ".join(reward_msg))
    
    def get_available_quests(self, character, npc_name=None):
        """
        获取可接取的任务列表
        
        Args:
            npc_name: NPC名称（如果指定，只返回该NPC的任务）
        
        Returns:
            list: 任务ID列表
        """
        available = []
        
        for quest_id, quest_data in GAME_DATA['quests'].items():
            # 检查NPC
            if npc_name:
                quest_giver = quest_data.get('quest_giver')
                if quest_giver != npc_name:
                    continue
            
            # 检查是否可接取
            can_accept, _ = self.can_accept_quest(character, quest_id)
            if can_accept:
                available.append(quest_id)
        
        return available
    
    def get_completable_quests(self, character, npc_name=None):
        """
        获取可完成的任务列表
        
        Args:
            npc_name: NPC名称
        
        Returns:
            list: 任务ID列表
        """
        completable = []
        active_quests = character.db.quests.get('active', [])
        
        for quest_instance in active_quests:
            quest_id = quest_instance['quest_id']
            quest_data = GAME_DATA['quests'].get(quest_id)
            
            if not quest_data:
                continue
            
            # 检查NPC
            if npc_name:
                finisher = quest_data.get('quest_finisher')
                if finisher != npc_name:
                    continue
            
            # 检查是否完成
            if self._check_quest_complete(quest_instance, quest_data):
                completable.append(quest_id)
        
        return completable

# 全局单例
QUEST_SYSTEM = QuestSystem()
