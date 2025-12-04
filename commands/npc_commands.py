# commands/npc_commands.py
"""
NPC交互命令 - 支持任务系统
"""
from evennia import Command
from world.systems.quest_system import QUEST_SYSTEM
from world.loaders.game_data import GAME_DATA

class CmdTalk(Command):
    """
    与NPC对话
    
    用法:
      talk <NPC名>
      对话 <NPC名>
    
    别名: talk, say, 对话
    """
    
    key = "talk"
    aliases = ["对话"]
    locks = "cmd:all()"
    help_category = "交互"
    
    def func(self):
        if not self.args.strip():
            self.caller.msg("用法: talk <NPC名>")
            return
        
        # 查找NPC
        npc = self.caller.search(self.args.strip())
        
        if not npc:
            return
        
        # 检查是否是NPC
        if not hasattr(npc, 'is_npc') or not npc.is_npc:
            self.caller.msg(f"{npc.key} 无法对话。")
            return
        
        # 触发对话事件
        self._handle_npc_dialogue(npc)
    
    def _handle_npc_dialogue(self, npc):
        """处理NPC对话"""
        npc_name = npc.key
        
        self.caller.msg(f"\n|c{'-' * 50}|n")
        self.caller.msg(f"|c与 {npc_name} 对话|n")
        self.caller.msg(f"|c{'-' * 50}|n")
        
        # 1. 检查可完成的任务
        completable = QUEST_SYSTEM.get_completable_quests(self.caller, npc_name)
        
        if completable:
            self.caller.msg(f"\n|g[!] {npc_name} 有任务可以交付:|n")
            
            for quest_id in completable:
                quest_data = GAME_DATA['quests'].get(quest_id)
                if quest_data:
                    quest_name = quest_data.get('name')
                    self.caller.msg(f"  |g✓|n {quest_name}")
                    self.caller.msg(f"     使用: |wcomplete {quest_name}|n")
            
            self.caller.msg("")
        
        # 2. 检查可接取的任务
        available = QUEST_SYSTEM.get_available_quests(self.caller, npc_name)
        
        if available:
            self.caller.msg(f"\n|y[!] {npc_name} 有新任务:|n")
            
            for quest_id in available:
                quest_data = GAME_DATA['quests'].get(quest_id)
                if quest_data:
                    quest_name = quest_data.get('name')
                    difficulty = quest_data.get('difficulty', '普通')
                    level = quest_data.get('level', 1)
                    
                    self.caller.msg(f"  |y?|n {quest_name} |w[Lv.{level} - {difficulty}]|n")
                    self.caller.msg(f"     使用: |waccept {quest_name}|n")
            
            self.caller.msg("")
        
        # 3. 触发任务系统的对话事件
        QUEST_SYSTEM.on_talk(self.caller, npc_name)
        
        # 4. 如果没有任务相关内容,显示默认对话
        if not completable and not available:
            # 显示NPC的默认对话(如果有配置)
            default_dialogue = npc.db.dialogue or f"{npc_name}: 你好,旅行者。"
            self.caller.msg(f"\n{default_dialogue}")
        
        self.caller.msg(f"|c{'-' * 50}|n\n")


class CmdNPCInfo(Command):
    """
    查看NPC信息
    
    用法:
      npcinfo <NPC名>
      查看 <NPC名>
    """
    
    key = "npcinfo"
    aliases = ["查看"]
    locks = "cmd:all()"
    help_category = "交互"
    
    def func(self):
        if not self.args.strip():
            self.caller.msg("用法: npcinfo <NPC名>")
            return
        
        # 查找NPC
        npc = self.caller.search(self.args.strip())
        
        if not npc:
            return
        
        # 检查是否是NPC
        if not hasattr(npc, 'is_npc') or not npc.is_npc:
            self.caller.msg(f"{npc.key} 不是NPC。")
            return
        
        # 显示NPC信息
        self.caller.msg(f"\n|c{'=' * 50}|n")
        self.caller.msg(f"|c{npc.key}|n")
        self.caller.msg(f"|c{'=' * 50}|n")
        
        # 基础信息
        if hasattr(npc.ndb, 'level'):
            self.caller.msg(f"等级: {npc.ndb.level}")
        
        if hasattr(npc.ndb, 'hp') and hasattr(npc.ndb, 'max_hp'):
            hp_percent = int((npc.ndb.hp / npc.ndb.max_hp) * 100)
            self.caller.msg(f"生命: {npc.ndb.hp}/{npc.ndb.max_hp} ({hp_percent}%)")
        
        # 描述
        if npc.db.desc:
            self.caller.msg(f"\n{npc.db.desc}")
        
        # 任务提示
        completable = QUEST_SYSTEM.get_completable_quests(self.caller, npc.key)
        available = QUEST_SYSTEM.get_available_quests(self.caller, npc.key)
        
        if completable or available:
            self.caller.msg(f"\n|y提示: 使用 'talk {npc.key}' 与其对话|n")
        
        self.caller.msg(f"|c{'=' * 50}|n\n")