# commands/dev/test_quest_cmd.py
"""
任务系统测试命令
放到开发命令集中使用
"""
from evennia import Command
from world.systems.quest_system import QUEST_SYSTEM
from world.loaders.game_data import GAME_DATA

class CmdTestQuest(Command):
    """
    测试任务系统
    
    用法:
      @testquest           - 完整测试
      @testquest quick     - 快速测试
      @testquest reset     - 重置测试数据
    """
    
    key = "@testquest"
    locks = "cmd:perm(Developer)"
    help_category = "开发"
    
    def func(self):
        args = self.args.strip().lower()
        
        if args == "quick":
            self.quick_test()
        elif args == "reset":
            self.reset_test_data()
        else:
            self.full_test()
    
    def full_test(self):
        """完整测试"""
        self.caller.msg("\n|c" + "=" * 60 + "|n")
        self.caller.msg("|c任务系统完整测试|n")
        self.caller.msg("|c" + "=" * 60 + "|n\n")
        
        # 初始化测试数据
        self._init_test_data()
        
        # 测试1: 接取任务
        self.caller.msg("|y[测试1] 接取新手任务|n")
        success, result = QUEST_SYSTEM.accept_quest(self.caller, "新手试炼_1")
        self.caller.msg(f"  结果: {'✓ ' + result if success else '✗ ' + result}\n")
        
        # 测试2: 模拟击杀
        self.caller.msg("|y[测试2] 模拟击杀5只野猪|n")
        for i in range(5):
            QUEST_SYSTEM.on_kill(self.caller, "野猪")
        self.caller.msg("  ✓ 击杀完成\n")
        
        # 测试3: 查看进度
        self.caller.msg("|y[测试3] 查看任务进度|n")
        active = self.caller.db.quests.get('active', [])
        if active:
            quest = active[0]
            quest_data = GAME_DATA['quests'].get(quest['quest_id'])
            is_done = QUEST_SYSTEM._check_quest_complete(quest, quest_data)
            self.caller.msg(f"  任务状态: {'可完成' if is_done else '进行中'}\n")
        
        # 测试4: 完成任务
        self.caller.msg("|y[测试4] 完成任务|n")
        success, result = QUEST_SYSTEM.complete_quest(self.caller, "新手试炼_1")
        self.caller.msg(f"  结果: {'✓ ' + result if success else '✗ ' + result}\n")
        
        # 测试5: 检查奖励
        self.caller.msg("|y[测试5] 检查奖励|n")
        inventory = getattr(self.caller.ndb, 'inventory', {})
        self.caller.msg(f"  背包物品: {len(inventory)}\n")
        for item, count in inventory.items():
            self.caller.msg(f"    - {item} x{count}")
        
        self.caller.msg("\n|g测试完成!|n\n")
    
    def quick_test(self):
        """快速测试"""
        self.caller.msg("\n|y快速测试模式|n\n")
        
        self._init_test_data()
        
        # 接取并立即完成任务
        QUEST_SYSTEM.accept_quest(self.caller, "新手试炼_1")
        
        # 模拟完成目标
        for i in range(5):
            QUEST_SYSTEM.on_kill(self.caller, "野猪")
        
        # 完成任务
        QUEST_SYSTEM.complete_quest(self.caller, "新手试炼_1")
        
        self.caller.msg("|g快速测试完成! 使用 'quests done' 查看已完成任务|n\n")
    
    def reset_test_data(self):
        """重置测试数据"""
        self.caller.db.quests = {
            'active': [],
            'completed': [],
            'failed': [],
            'daily_completed': {}
        }
        self.caller.ndb.inventory = {}
        self.caller.ndb.skills = []
        
        self.caller.msg("|g任务数据已重置|n\n")
    
    def _init_test_data(self):
        """初始化测试数据"""
        if not hasattr(self.caller.db, 'quests') or self.caller.db.quests is None:
            self.caller.db.quests = {
                'active': [],
                'completed': [],
                'failed': [],
                'daily_completed': {}
            }
        
        if not hasattr(self.caller.ndb, 'level'):
            self.caller.ndb.level = 1
        if not hasattr(self.caller.ndb, 'realm'):
            self.caller.ndb.realm = "炼气期"
        if not hasattr(self.caller.ndb, 'inventory'):
            self.caller.ndb.inventory = {}
        if not hasattr(self.caller.ndb, 'skills'):
            self.caller.ndb.skills = []