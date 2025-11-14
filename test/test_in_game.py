#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
游戏内技能系统测试脚本
此脚本可以直接在游戏内运行，用于测试技能系统是否正常工作
"""

def test_skill_system_in_game(caller):
    """
    在游戏内测试技能系统
    """
    # 显示欢迎信息
    caller.msg("|g=== 技能系统游戏内测试 ===|n")
    
    # 1. 学习火球术
    caller.msg("|w1. 学习火球术...|n")
    if not caller.db.skills:
        caller.db.skills = {}
    caller.db.skills["fire.fireball"] = {"level": 3}  # 设置为3级
    caller.msg("✓ 已学会火球术（3级）")
    
    # 2. 创建测试目标
    caller.msg("|w2. 创建测试目标...|n")
    from evennia import create_object
    from typeclasses.characters import Character
    
    # 创建一个测试目标
    target = create_object(Character, key="测试木桩", location=caller.location)
    target.db.hp = 100  # 设置100点HP
    caller.msg(f"✓ 已创建测试目标: {target.key} (HP: {target.db.hp})")
    
    # 3. 设置目标
    caller.msg("|w3. 设置攻击目标...|n")
    caller.db.target = target
    caller.msg(f"✓ 已将 {target.key} 设为目标")
    
    # 4. 施放火球术
    caller.msg("|w4. 施放火球术...|n")
    from commands.cast import CmdCast
    cmd = CmdCast()
    cmd.caller = caller
    cmd.args = "fire.fireball"
    cmd.func()
    
    # 5. 显示结果
    caller.msg("|w5. 检查结果...|n")
    caller.msg(f"目标剩余HP: {target.db.hp}")
    
    # 6. 清理
    caller.msg("|w6. 清理测试目标...|n")
    target.delete()
    caller.msg("✓ 测试目标已清理")
    
    # 7. 总结
    caller.msg("|g=== 测试完成 ===|n")
    caller.msg("|g如果看到以上信息且没有错误，说明技能系统工作正常！|n")

# 为方便游戏内调用，添加一个简短的别名
test = test_skill_system_in_game

if __name__ == "__main__":
    # 这部分只在直接运行脚本时执行
    print("此脚本需要在游戏内运行，使用方法：")
    print("@py import test_in_game; test_in_game.test_skill_system_in_game(self)")