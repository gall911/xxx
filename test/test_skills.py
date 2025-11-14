"""
技能系统测试脚本

使用方法：
1. 在游戏中加载此脚本: @py import test_skills; test_skills.setup_test_character()
2. 测试技能: @py import test_skills; test_skills.test_skills()

注意：测试前请确保已创建一个测试角色
"""

def setup_test_character():
    """设置测试角色"""
    # 获取当前角色
    me = __import__('evennia').search_script('me').get()
    
    # 初始化角色属性
    me.db.skills = {
        "fire.fireball": {"level": 3},
        "ice.iceblast": {"level": 1},
        "sword.slash": {"level": 2}
    }
    
    me.db.hp = 100
    me.db.max_hp = 100
    me.db.mp = 100
    me.db.max_mp = 100
    
    me.msg("测试角色设置完成！")
    me.msg(f"技能: {me.db.skills}")
    me.msg(f"HP: {me.db.hp}/{me.db.max_hp}, MP: {me.db.mp}/{me.db.max_mp}")

def test_skills():
    """测试技能系统"""
    me = __import__('evennia').search_script('me').get()
    
    # 创建一个测试目标
    from evennia import create_object
    from typeclasses.characters import Character
    
    if not hasattr(me.location.db, 'test_target'):
        target = create_object(Character, key="测试木桩")
        target.location = me.location
        target.db.hp = 200
        target.db.max_hp = 200
        me.location.db.test_target = target
        me.msg(f"创建了测试目标: {target.key}")
    else:
        target = me.location.db.test_target
        me.msg(f"使用已有测试目标: {target.key}")
    
    # 设置目标
    me.db.target = target
    
    # 测试技能
    me.msg("开始测试技能...")
    
    # 测试火球术
    me.execute_cmd('cast fire.fireball')
    
    # 测试冰爆术
    me.execute_cmd('cast ice.iceblast')
    
    # 测试斩击
    me.execute_cmd('cast sword.slash')
    
    # 显示目标状态
    me.msg(f"测试目标HP: {target.db.hp}/{target.db.max_hp}")
    
    # 显示技能列表
    me.execute_cmd('skills')