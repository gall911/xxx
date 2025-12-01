# world/test_setup.py
"""
快速测试脚本
用于测试游戏系统是否正常工作
"""

def test_combat_system():
    """测试战斗系统"""
    from world.systems.combat_system import CombatSystem
    from evennia import create_object
    from typeclasses.characters import Character
    
    print("\n=== 测试战斗系统 ===")
    
    # 创建测试角色
    player = create_object(Character, key="测试玩家")
    enemy = create_object(Character, key="测试敌人")
    
    # 初始化属性
    player.ndb.hp = 100
    player.ndb.max_hp = 100
    player.ndb.qi = 50
    player.ndb.max_qi = 50
    player.ndb.strength = 20
    player.ndb.skills = ['普通攻击']
    
    enemy.ndb.hp = 80
    enemy.ndb.max_hp = 80
    enemy.ndb.qi = 30
    enemy.ndb.max_qi = 30
    enemy.ndb.strength = 15
    enemy.ndb.skills = ['普通攻击']
    
    # 测试战斗
    combat = CombatSystem()
    combat.start_combat(player, enemy)
    
    # 执行几回合
    for i in range(3):
        print(f"\n--- 回合 {i+1} ---")
        result = combat.execute_combat_round(player, enemy)
        
        for msg in result['messages']:
            print(msg)
        
        print(f"玩家HP: {player.ndb.hp}/{player.ndb.max_hp}")
        print(f"敌人HP: {enemy.ndb.hp}/{enemy.ndb.max_hp}")
        
        if result['combat_end']:
            print(f"\n战斗结束！获胜者: {result['winner'].key}")
            break
    
    # 清理
    player.delete()
    enemy.delete()
    
    print("\n战斗系统测试完成！")

def test_data_loading():
    """测试数据加载"""
    from world.loaders.game_data import GAME_DATA
    
    print("\n=== 测试数据加载 ===")
    print(f"境界数量: {len(GAME_DATA['realms'])}")
    print(f"技能数量: {len(GAME_DATA['skills'])}")
    print(f"物品数量: {len(GAME_DATA['items'])}")
    print(f"NPC数量: {len(GAME_DATA['npcs'])}")
    print(f"房间数量: {len(GAME_DATA['rooms'])}")
    
    # 显示部分数据
    if GAME_DATA['realms']:
        print("\n境界列表:")
        for realm_name in list(GAME_DATA['realms'].keys())[:3]:
            print(f"  - {realm_name}")
    
    if GAME_DATA['skills']:
        print("\n技能列表:")
        for skill_name in list(GAME_DATA['skills'].keys())[:5]:
            print(f"  - {skill_name}")
    
    print("\n数据加载测试完成！")

def run_all_tests():
    """运行所有测试"""
    test_data_loading()
    test_combat_system()
