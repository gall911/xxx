"""
任务系统命令
"""
from evennia import Command
from world.systems.quest_system import QUEST_SYSTEM
from world.loaders.game_data import GAME_DATA

class CmdQuest(Command):
    """
    查看任务详情
    
    用法:
      quest              - 查看所有活跃任务
      quest <任务名/ID>  - 查看指定任务详情
    
    别名: task
    """
    
    key = "quest"
    aliases = ["task", "任务"]
    locks = "cmd:all()"
    help_category = "任务"
    
    def func(self):
        character = self.caller
        
        # 初始化任务数据
        if not hasattr(character.db, 'quests') or character.db.quests is None:
            character.db.quests = {
                'active': [],
                'completed': [],
                'failed': [],
                'daily_completed': {}
            }
        
        active_quests = character.db.quests.get('active', [])
        
        if not self.args.strip():
            # 显示所有活跃任务
            if not active_quests:
                self.caller.msg("|y当前没有进行中的任务|n")
                return
            
            self.caller.msg("|c" + "=" * 60 + "|n")
            self.caller.msg("|c当前任务|n")
            self.caller.msg("|c" + "=" * 60 + "|n")
            
            for i, quest_instance in enumerate(active_quests, 1):
                quest_id = quest_instance['quest_id']
                quest_data = GAME_DATA['quests'].get(quest_id)
                
                if not quest_data:
                    continue
                
                quest_name = quest_data.get('name', quest_id)
                difficulty = quest_data.get('difficulty', '普通')
                
                # 检查完成状态
                all_completed = QUEST_SYSTEM._check_quest_complete(quest_instance, quest_data)
                status = "|g[可交付]|n" if all_completed else "|y[进行中]|n"
                
                self.caller.msg(f"{i}. {status} {quest_name} |w({difficulty})|n")
                
                # 显示目标进度
                from world.systems.quest_objectives import get_objective_handler
                for objective in quest_instance['objectives']:
                    handler = get_objective_handler(objective.get('type'))
                    if handler:
                        progress = handler.get_progress_text(objective)
                        completed = "|g✓|n" if handler.is_completed(objective) else "|r✗|n"
                        self.caller.msg(f"   {completed} {progress}")
            
            self.caller.msg("|c" + "=" * 60 + "|n")
            self.caller.msg("|w提示: 使用 'quest <任务名>' 查看详情|n")
            
        else:
            # 查看指定任务详情
            quest_query = self.args.strip()
            
            # 查找任务
            quest_instance = None
            quest_data = None
            
            for q in active_quests:
                qid = q['quest_id']
                qdata = GAME_DATA['quests'].get(qid)
                
                if qdata and (qdata.get('name') == quest_query or qid == quest_query):
                    quest_instance = q
                    quest_data = qdata
                    break
            
            if not quest_data:
                self.caller.msg(f"|r未找到任务: {quest_query}|n")
                return
            
            # 显示详情
            self._show_quest_detail(quest_instance, quest_data)
    
    def _show_quest_detail(self, quest_instance, quest_data):
        """显示任务详情"""
        name = quest_data.get('name', '未知任务')
        description = quest_data.get('description', '无描述').strip()
        difficulty = quest_data.get('difficulty', '普通')
        level = quest_data.get('level', 1)
        quest_type = quest_data.get('type', 'unknown')
        
        self.caller.msg("|c" + "=" * 60 + "|n")
        self.caller.msg(f"|c{name}|n |w[Lv.{level} - {difficulty}]|n")
        self.caller.msg("|c" + "=" * 60 + "|n")
        self.caller.msg(description)
        self.caller.msg("")
        self.caller.msg("|y任务目标:|n")
        
        # 显示所有目标
        from world.systems.quest_objectives import get_objective_handler
        for objective in quest_instance['objectives']:
            handler = get_objective_handler(objective.get('type'))
            if handler:
                progress = handler.get_progress_text(objective)
                completed = "|g✓|n" if handler.is_completed(objective) else "|r✗|n"
                self.caller.msg(f"  {completed} {progress}")
        
        # 显示奖励
        rewards = quest_data.get('rewards', {})
        if rewards:
            self.caller.msg("")
            self.caller.msg("|y任务奖励:|n")
            
            reward_parts = []
            if rewards.get('exp'):
                reward_parts.append(f"经验 +{rewards['exp']}")
            if rewards.get('gold'):
                reward_parts.append(f"金币 +{rewards['gold']}")
            
            for item in rewards.get('items', []):
                item_name = item.get('name')
                item_count = item.get('count', 1)
                reward_parts.append(f"{item_name} x{item_count}")
            
            for skill in rewards.get('unlock_skills', []):
                reward_parts.append(f"学会技能: {skill}")
            
            if reward_parts:
                self.caller.msg("  " + ", ".join(reward_parts))
        
        # 显示任务给予者/完成者
        giver = quest_data.get('quest_giver')
        finisher = quest_data.get('quest_finisher')
        
        if giver or finisher:
            self.caller.msg("")
            if giver:
                self.caller.msg(f"|y任务发布: |w{giver}|n")
            if finisher:
                self.caller.msg(f"|y任务交付: |w{finisher}|n")
        
        self.caller.msg("|c" + "=" * 60 + "|n")

class CmdQuestList(Command):
    """
    查看任务列表
    
    用法:
      quests          - 查看所有任务
      quests active   - 查看进行中的任务
      quests done     - 查看已完成的任务
      quests daily    - 查看每日任务
    
    别名: questlog
    """
    
    key = "quests"
    aliases = ["questlog", "任务列表"]
    locks = "cmd:all()"
    help_category = "任务"
    
    def func(self):
        character = self.caller
        
        # 初始化任务数据
        if not hasattr(character.db, 'quests') or character.db.quests is None:
            character.db.quests = {
                'active': [],
                'completed': [],
                'failed': [],
                'daily_completed': {}
            }
        
        args = self.args.strip().lower()
        
        if args == 'done' or args == 'completed':
            self._show_completed()
        elif args == 'daily':
            self._show_daily()
        else:
            self._show_active()
    
    def _show_active(self):
        """显示进行中的任务"""
        active_quests = self.caller.db.quests.get('active', [])
        
        if not active_quests:
            self.caller.msg("|y当前没有进行中的任务|n")
            return
        
        self.caller.msg("|c" + "=" * 60 + "|n")
        self.caller.msg("|c进行中的任务|n")
        self.caller.msg("|c" + "=" * 60 + "|n")
        
        for quest_instance in active_quests:
            quest_id = quest_instance['quest_id']
            quest_data = GAME_DATA['quests'].get(quest_id)
            
            if not quest_data:
                continue
            
            name = quest_data.get('name', quest_id)
            difficulty = quest_data.get('difficulty', '普通')
            level = quest_data.get('level', 1)
            
            all_done = QUEST_SYSTEM._check_quest_complete(quest_instance, quest_data)
            status = "|g[可交付]|n" if all_done else "|y[进行中]|n"
            
            self.caller.msg(f"{status} {name} |w[Lv.{level} - {difficulty}]|n")
        
        self.caller.msg("|c" + "=" * 60 + "|n")
    
    def _show_completed(self):
        """显示已完成的任务"""
        completed = self.caller.db.quests.get('completed', [])
        
        if not completed:
            self.caller.msg("|y还没有完成过任务|n")
            return
        
        self.caller.msg("|c" + "=" * 60 + "|n")
        self.caller.msg("|c已完成的任务|n")
        self.caller.msg("|c" + "=" * 60 + "|n")
        
        for quest_id in completed:
            quest_data = GAME_DATA['quests'].get(quest_id)
            if quest_data:
                name = quest_data.get('name', quest_id)
                self.caller.msg(f"|g✓|n {name}")
        
        self.caller.msg("|c" + "=" * 60 + "|n")
        self.caller.msg(f"|w总计: {len(completed)} 个任务|n")
    
    def _show_daily(self):
        """显示每日任务"""
        import datetime
        today = datetime.date.today().isoformat()
        
        daily_completed = self.caller.db.quests.get('daily_completed', {}).get(today, [])
        
        # 查找所有每日任务
        all_daily = []
        for quest_id, quest_data in GAME_DATA['quests'].items():
            if quest_data.get('daily', False):
                all_daily.append((quest_id, quest_data))
        
        if not all_daily:
            self.caller.msg("|y没有可用的每日任务|n")
            return
        
        self.caller.msg("|c" + "=" * 60 + "|n")
        self.caller.msg("|c每日任务|n")
        self.caller.msg("|c" + "=" * 60 + "|n")
        
        for quest_id, quest_data in all_daily:
            name = quest_data.get('name', quest_id)
            
            if quest_id in daily_completed:
                self.caller.msg(f"|g✓|n {name} |w(今日已完成)|n")
            else:
                self.caller.msg(f"|y○|n {name}")
        
        self.caller.msg("|c" + "=" * 60 + "|n")
        self.caller.msg(f"|w今日完成: {len(daily_completed)}/{len(all_daily)}|n")

class CmdAbandon(Command):
    """
    放弃任务
    
    用法:
      abandon <任务名/ID>
    
    别名: drop
    """
    
    key = "abandon"
    aliases = ["drop", "放弃"]
    locks = "cmd:all()"
    help_category = "任务"
    
    def func(self):
        if not self.args.strip():
            self.caller.msg("用法: abandon <任务名>")
            return
        
        quest_query = self.args.strip()
        
        # 查找任务ID
        active_quests = self.caller.db.quests.get('active', [])
        quest_id = None
        
        for quest in active_quests:
            qid = quest['quest_id']
            qdata = GAME_DATA['quests'].get(qid)
            
            if qdata and (qdata.get('name') == quest_query or qid == quest_query):
                quest_id = qid
                break
        
        if not quest_id:
            self.caller.msg(f"|r未找到任务: {quest_query}|n")
            return
        
        # 放弃任务
        success, quest_name = QUEST_SYSTEM.abandon_quest(self.caller, quest_id)
        
        if success:
            self.caller.msg(f"|y已放弃任务: {quest_name}|n")
        else:
            self.caller.msg(f"|r{quest_name}|n")

class CmdAcceptQuest(Command):
    """
    接取任务 (通常由NPC对话触发)
    
    用法:
      accept <任务名/ID>
    """
    
    key = "accept"
    aliases = ["接取"]
    locks = "cmd:all()"
    help_category = "任务"
    
    def func(self):
        if not self.args.strip():
            self.caller.msg("用法: accept <任务名>")
            return
        
        quest_query = self.args.strip()
        
        # 查找任务ID
        quest_id = None
        for qid, qdata in GAME_DATA['quests'].items():
            if qdata.get('name') == quest_query or qid == quest_query:
                quest_id = qid
                break
        
        if not quest_id:
            self.caller.msg(f"|r未找到任务: {quest_query}|n")
            return
        
        # 接取任务
        success, result = QUEST_SYSTEM.accept_quest(self.caller, quest_id)
        
        if success:
            self.caller.msg(f"|g已接取任务: {result}|n")
            self.caller.msg("|w使用 'quest' 命令查看任务详情|n")
        else:
            self.caller.msg(f"|r无法接取: {result}|n")

class CmdCompleteQuest(Command):
    """
    完成任务 (通常由NPC对话触发)
    """
    
    key = "complete"
    aliases = ["finish", "完成"]
    locks = "cmd:all()"
    help_category = "任务"
    
    def func(self):
        if not self.args.strip():
            self.caller.msg("用法: complete <任务名>")
            return
        
        quest_query = self.args.strip()
        
        # 查找任务ID
        active_quests = self.caller.db.quests.get('active', [])
        quest_id = None
        
        for quest in active_quests:
            qid = quest['quest_id']
            qdata = GAME_DATA['quests'].get(qid)
            
            if qdata and (qdata.get('name') == quest_query or qid == quest_query):
                quest_id = qid
                break
        
        if not quest_id:
            self.caller.msg(f"|r未找到任务: {quest_query}|n")
            return
        
        # 完成任务
        success, result = QUEST_SYSTEM.complete_quest(self.caller, quest_id)
        
        if success:
            self.caller.msg(f"|g恭喜! 完成任务: {result}|n")
        else:
            self.caller.msg(f"|r{result}|n")
            # --- START OF FILE quest_commands.py ---
# ... (保留你上面写的所有的 import 和 Command 类) ...

# ... 在文件的最下面添加以下代码 ...

from evennia import CmdSet

class QuestCmdSet(CmdSet):
    """
    任务系统命令集
    """
    key = "QuestCmdSet"
    
    def at_cmdset_creation(self):
        self.add(CmdQuest())
        self.add(CmdQuestList())
        self.add(CmdAbandon())
        self.add(CmdAcceptQuest())
        self.add(CmdCompleteQuest())