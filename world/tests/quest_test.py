"""
任务系统测试脚本
在Evennia中运行: py self.execute_cmd("@py world.tests.quest_test")
或者直接在代码中调用测试函数
"""

from world.systems.quest_system import QUEST_SYSTEM
from world.loaders.game_data import GAME_DATA
from evennia.utils import logger

def test_quest_system(character):
    """
    完整任务系统测试
    
    使用方法:
    1. 在游戏中: @py from world.tests.quest_test import test_quest_system; test_quest_system(self)
    2. 或创建测试命令调用此函数
    """
    
    logger.log_info("=" * 60)
    logger.log_info("开始任务系统测试")
    logger.log_info("=" * 60)
    
    # 初始化测试角色数据
    if not hasattr(character.db, 'quests'):
        character.db.quests = {
            'active': [],
            'completed': [],
            'failed': [],
            'daily_completed': {}
        }
    
    # 初始化测试属性
    if not hasattr(character.ndb, 'level'):
        character.ndb.level = 1
    if not hasattr(character.ndb, 'realm'):
        character.ndb.realm = "炼气期"
    if not hasattr(character.ndb, 'inventory'):
        character.ndb.inventory = {}
    if not hasattr(character.ndb, 'skills'):
        character.ndb.skills = []
    
    character.msg("\n|c=== 任务系统测试开始 ===|n\n")
    
    # ========================================
    # 测试1: 查看可用任务
    # ========================================
    character.msg("|y[测试1] 查看可用任务|n")
    
    available = QUEST_SYSTEM.get_available_quests(character)
    character.msg(f"当前可接取任务数: {len(available)}")
    
    for quest_id in available[:3]:  # 只显示前3个
        quest_data = GAME_DATA['quests'].get(quest_id)
        if quest_data:
            character.msg(f"  - {quest_data.get('name')} (ID: {quest_id})")
    
    character.msg("")
    
    # ========================================
    # 测试2: 接取新手任务
    # ========================================
    character.msg("|y[测试2] 接取新手任务|n")
    
    test_quest_id = "newbie_trial_1"  # 新手试炼_1
    
    success, result = QUEST_SYSTEM.accept_quest(character, test_quest_id)
    
    if success:
        character.msg(f"|g✓ 成功接取: {result}|n")
    else:
        character.msg(f"|r✗ 接取失败: {result}|n")
    
    character.msg("")
    
    # ========================================
    # 测试3: 查看活跃任务
    # ========================================
    character.msg("|y[测试3] 查看活跃任务|n")
    
    active_quests = character.db.quests.get('active', [])
    character.msg(f"活跃任务数: {len(active_quests)}")
    
    for quest in active_quests:
        quest_data = GAME_DATA['quests'].get(quest['quest_id'])
        if quest_data:
            character.msg(f"  - {quest_data.get('name')}")
            
            # 显示目标
            from world.systems.quest_objectives import get_objective_handler
            for obj in quest['objectives']:
                handler = get_objective_handler(obj.get('type'))
                if handler:
                    progress = handler.get_progress_text(obj)
                    character.msg(f"    {progress}")
    
    character.msg("")
    
    # ========================================
    # 测试4: 模拟击杀事件
    # ========================================
    character.msg("|y[测试4] 模拟击杀野猪|n")
    
    # 模拟击杀5只野猪
    for i in range(5):
        QUEST_SYSTEM.on_kill(character, "野猪")
        character.msg(f"  击杀野猪 #{i+1}")
    
    character.msg("")
    
    # ========================================
    # 测试5: 检查任务进度
    # ========================================
    character.msg("|y[测试5] 检查任务进度|n")
    
    active_quests = character.db.quests.get('active', [])
    
    for quest in active_quests:
        quest_data = GAME_DATA['quests'].get(quest['quest_id'])
        if quest_data:
            is_complete = QUEST_SYSTEM._check_quest_complete(quest, quest_data)
            status = "|g可完成|n" if is_complete else "|y进行中|n"
            
            character.msg(f"{quest_data.get('name')}: {status}")
    
    character.msg("")
    
    # ========================================
    # 测试6: 完成任务
    # ========================================
    character.msg("|y[测试6] 尝试完成任务|n")
    
    if active_quests:
        quest_id = active_quests[0]['quest_id']
        success, result = QUEST_SYSTEM.complete_quest(character, quest_id)
        
        if success:
            character.msg(f"|g✓ 任务完成: {result}|n")
        else:
            character.msg(f"|r✗ 无法完成: {result}|n")
    
    character.msg("")
    
    # ========================================
    # 测试7: 查看已完成任务
    # ========================================
    character.msg("|y[测试7] 查看已完成任务|n")
    
    completed = character.db.quests.get('completed', [])
    character.msg(f"已完成任务数: {len(completed)}")
    
    for quest_id in completed:
        quest_data = GAME_DATA['quests'].get(quest_id)
        if quest_data:
            character.msg(f"  ✓ {quest_data.get('name')}")
    
    character.msg("")
    
    # ========================================
    # 测试8: 测试任务链
    # ========================================
    character.msg("|y[测试8] 测试任务链解锁|n")
    
    # 检查是否解锁了下一个任务
    available = QUEST_SYSTEM.get_available_quests(character)
    
    for quest_id in available:
        quest_data = GAME_DATA['quests'].get(quest_id)
        if quest_data and quest_data.get('name') == "收集灵草":
            character.msg(f"|g✓ 任务链生效: {quest_data.get('name')} 已解锁|n")
            break
    else:
        character.msg("|y任务链未触发或已接取|n")
    
    character.msg("")
    
    # ========================================
    # 测试9: 测试每日任务
    # ========================================
    character.msg("|y[测试9] 测试每日任务|n")
    
    daily_quest_id = "daily_cultivation"
    
    can_accept, reason = QUEST_SYSTEM.can_accept_quest(character, daily_quest_id)
    
    if can_accept:
        success, result = QUEST_SYSTEM.accept_quest(character, daily_quest_id)
        if success:
            character.msg(f"|g✓ 接取每日任务: {result}|n")
    else:
        character.msg(f"|y每日任务状态: {reason}|n")
    
    character.msg("")
    
    # ========================================
    # 测试10: 测试放弃任务
    # ========================================
    character.msg("|y[测试10] 测试放弃任务|n")
    
    active_quests = character.db.quests.get('active', [])
    
    if active_quests:
        quest_id = active_quests[0]['quest_id']
        quest_data = GAME_DATA['quests'].get(quest_id)
        
        success, result = QUEST_SYSTEM.abandon_quest(character, quest_id)
        
        if success:
            character.msg(f"|g✓ 放弃任务: {result}|n")
        else:
            character.msg(f"|r✗ {result}|n")
    else:
        character.msg("|y没有可放弃的任务|n")
    
    character.msg("")
    
    # ========================================
    # 测试总结
    # ========================================
    character.msg("\n|c=== 任务系统测试完成 ===|n\n")
    
    character.msg("|g测试结果总结:|n")
    character.msg(f"  当前活跃任务: {len(character.db.quests.get('active', []))}")
    character.msg(f"  已完成任务: {len(character.db.quests.get('completed', []))}")
    character.msg(f"  背包物品: {len(character.ndb.inventory)}")
    character.msg(f"  已学技能: {len(character.ndb.skills)}")
    
    logger.log_info("任务系统测试完成")
    logger.log_info("=" * 60)


def quick_test_objectives(character):
    """
    快速测试所有目标类型
    """
    character.msg("\n|c=== 快速目标类型测试 ===|n\n")
    
    from world.systems.quest_objectives import get_objective_handler
    
    # 测试所有目标类型
    test_objectives = [
        {
            'type': 'kill',
            'target': '测试怪物',
            'count': 10,
            'current': 3
        },
        {
            'type': 'collect',
            'target': '测试物品',
            'count': 5,
            'current': 2
        },
        {
            'type': 'talk',
            'target': '测试NPC',
            'talked': False
        },
        {
            'type': 'explore',
            'target': '测试地点',
            'visited': True
        },
        {
            'type': 'cultivate',
            'duration': 1800,
            'current': 900
        },
        {
            'type': 'use_skill',
            'target': '测试技能',
            'count': 50,
            'current': 25
        },
        {
            'type': 'craft',
            'target': '测试道具',
            'count': 3,
            'current': 1
        }
    ]
    
    for obj in test_objectives:
        handler = get_objective_handler(obj['type'])
        if handler:
            progress = handler.get_progress_text(obj)
            is_done = handler.is_completed(obj)
            status = "|g✓|n" if is_done else "|y○|n"
            
            character.msg(f"{status} [{obj['type']}] {progress}")
    
    character.msg("\n|g所有目标类型测试完成|n\n")


def test_quest_requirements(character):
    """
    测试任务需求检查
    """
    character.msg("\n|c=== 任务需求测试 ===|n\n")
    
    # 保存原始数据
    original_level = character.ndb.level if hasattr(character.ndb, 'level') else 1
    original_realm = character.ndb.realm if hasattr(character.ndb, 'realm') else "炼气期"
    
    test_cases = [
        ("等级不足", {"level": 1, "realm": "炼气期", "quest": "天命之路_1"}),
        ("等级足够", {"level": 5, "realm": "筑基期", "quest": "天命之路_1"}),
        ("境界不符", {"level": 10, "realm": "炼气期", "quest": "铸剑师的请求"}),
    ]
    
    for test_name, test_data in test_cases:
        character.ndb.level = test_data['level']
        character.ndb.realm = test_data['realm']
        
        can_accept, reason = QUEST_SYSTEM.can_accept_quest(character, test_data['quest'])
        
        status = "|g✓|n" if can_accept else "|r✗|n"
        character.msg(f"{status} {test_name}: {reason if not can_accept else '可以接取'}")
    
    # 恢复原始数据
    character.ndb.level = original_level
    character.ndb.realm = original_realm
    
    character.msg("\n|g需求测试完成|n\n")


# ========================================
# 命令封装（可选）
# ========================================

from evennia import Command

class CmdTestQuest(Command):
    """
    测试任务系统
    
    用法:
      @testquest           - 完整测试
      @testquest obj       - 测试目标类型
      @testquest req       - 测试需求检查
    """
    
    key = "@testquest"
    locks = "cmd:perm(Developer)"
    help_category = "开发"
    
    def func(self):
        args = self.args.strip().lower()
        
        if args == "obj":
            quick_test_objectives(self.caller)
        elif args == "req":
            test_quest_requirements(self.caller)
        else:
            test_quest_system(self.caller)