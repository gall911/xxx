"""
火球术测试脚本
"""

def test_fireball():
    """
    测试火球术功能
    """
    # 获取当前角色
    caller = self
    
    # 确保角色有db属性
    if not hasattr(caller, 'db'):
        caller.db = type('obj', (object,), {})()
    
    # 初始化技能字典
    if not hasattr(caller.db, 'skills') or not caller.db.skills:
        caller.db.skills = {}
    
    # 添加火球术技能（3级）
    caller.db.skills["fire.fireball"] = {"level": 3}
    
    # 创建一个测试目标
    from evennia import create_object
    target = create_object("typeclasses.characters.Character", key="测试木桩", location=caller.location)
    target.db.hp = 100
    
    # 设置为目标
    caller.db.target = target
    
    # 导入并执行cast命令
    from commands.cast import CmdCast
    cmd = CmdCast()
    cmd.caller = caller
    cmd.args = "fire.fireball"
    cmd.func()
    
    # 显示结果
    caller.msg(f"测试完成！目标剩余HP: {target.db.hp}")
    
    # 清理目标
    target.delete()
    
    return True

# 为游戏内使用提供别名
run = test_fireball