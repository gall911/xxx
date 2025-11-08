"""
仙侠风格移动命令

使用方法:
    北/南/东/西/东北/西北/东南/西南/上/下/里/外
"""

import random
from evennia import Command, default_cmds
from typeclasses.rooms import Room
from utils.theme_utils import color_room_name

class XianyaMoveCommand(default_cmds.MuxCommand):
    """
    仙侠风格移动命令
    
    使用方法:
        北/南/东/西/东北/西北/东南/西南/上/下/里/外
    """
    
    # 室内移动描述
    INDOOR_MOVES = [
        "掐动法诀，身形化作一缕青烟，自{from_room}飘然而出，须臾间已至{to_room}",
        "足下生莲，步步生辉，自{from_room}缓步而出，转瞬已出现在{to_room}之中",
        "袖袍一挥，空间微颤，自{from_room}瞬间转移至{to_room}，宛若从未移动",
        "身形一晃，化作流光自{from_room}射出，眨眼间已端坐于{to_room}内",
        "掐诀念咒，自{from_room}凭空消失，下一刻已出现在{to_room}中央",
        "足踏七星，身形飘忽，自{from_room}悠然飘出，转瞬已立于{to_room}内",
        "仙气缭绕，身影渐淡，自{from_room}消散无形，转瞬已在{to_room}现身",
        "道袍轻摆，步步生莲，自{from_room}踏空而行，转眼已至{to_room}",
        "手捏法印，口诵真言，自{from_room}化作一道神光，瞬息已抵{to_room}",
        "剑指轻点，身随心动，自{from_room}飘然起舞，转瞬已至{to_room}",
        "灵光一闪，身形变幻，自{from_room}遁入虚空，须臾已现{to_room}",
        "仙音渺渺，祥云缭绕，自{from_room}乘风而去，转眼已至{to_room}"
    ]
    
    # 室外移动描述
    OUTDOOR_MOVES = [
        "御剑而起，自{from_room}冲天而起，化作长虹直入{to_room}",
        "驾云而行，自{from_room}缓缓升起，飘然落于{to_room}",
        "身形一晃，化作遁光自{from_room}射出，瞬息间已立于{to_room}",
        "足下生风，自{from_room}飘然而起，转瞬间已落于{to_room}之前",
        "掐动遁术，自{from_room}化作流光消失，下一刻已出现在{to_room}入口",
        "袖袍鼓荡，自{from_room}腾空而起，如飞仙般飘向{to_room}方向",
        "腾云驾雾，自{from_room}破空而去，转眼已至{to_room}上空",
        "脚踏祥云，自{from_room}冉冉升起，顷刻已至{to_room}",
        "剑气纵横，自{from_room}化作一道剑光，瞬息已抵{to_room}",
        "仙鹤为骑，自{from_room}乘风而去，转瞬已至{to_room}",
        "风雷之声，自{from_room}破空而去，转眼已至{to_room}",
        "踏月而行，自{from_room}凌空而起，须臾已至{to_room}"
    ]
    
    # 撞墙描述
    BUMP_DESCRIPTIONS = [
        "前方似乎有结界阻拦，无法通过。",
        "你尝试前行，却被无形的力量挡了回来。",
        "此地被仙法禁制，无法通行。",
        "前方道路被阵法封锁，无法通过。",
        "你感到一股强大的阻力，无法前进。",
        "前方有仙气缭绕，似有禁制守护，不得通过。",
        "你试图前行，却撞在一道无形的屏障上，头晕目眩。",
        "前方灵气波动异常，似乎有强大禁法守护，无法通过。",
        "你尝试前行，却被一道金光弹回，前方有仙家阵法守护。",
        "前方空间扭曲，似有空间禁制，无法强行通过。",
        "你感到前方有强大灵力波动，似有高人布下禁制，无法通行。",
        "前方有仙雾缭绕，伸手不见五指，无法前行。"
    ]
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        if not self.args:
            return
            
        # 获取方向
        direction = self.args.strip()
        
        # 检查是否有对应的出口
        exit_obj = caller.search(direction, destination=caller.location)
        
        if not exit_obj:
            # 没有找到出口，输出撞墙描述
            caller.msg(random.choice(self.BUMP_DESCRIPTIONS))
            return
            
        # 检查出口是否可用
        if not exit_obj.access(caller, "traverse"):
            caller.msg(f"无法通过{exit_obj.key}。")
            return
            
        # 获取源房间和目标房间
        source_room = caller.location
        target_room = exit_obj.destination
        
        # 确定使用室内还是室外移动描述
        if source_room.is_indoor and target_room.is_indoor:
            move_descriptions = self.INDOOR_MOVES
        else:
            move_descriptions = self.OUTDOOR_MOVES
            
        # 随机选择一个移动描述
        move_desc = random.choice(move_descriptions)
        
        # 替换房间名（去掉编号）
        from_room_name = source_room.key.split('(')[0].strip()
        to_room_name = target_room.key.split('(')[0].strip()
        
        # 格式化移动描述
        move_desc = move_desc.format(
            from_room=from_room_name,
            to_room=to_room_name
        )
        
        # 移动角色
        caller.msg(f"你{move_desc}")
        caller.move_to(target_room)
        
        # 检查是否在移动后需要显示房间描述
        caller.execute_cmd("look")

# 为每个方向创建命令
class CmdNorth(XianyaMoveCommand):
    key = "北"
    aliases = ["north", "n"]

class CmdSouth(XianyaMoveCommand):
    key = "南"
    aliases = ["south", "s"]

class CmdEast(XianyaMoveCommand):
    key = "东"
    aliases = ["east", "e"]

class CmdWest(XianyaMoveCommand):
    key = "西"
    aliases = ["west", "w"]

class CmdNortheast(XianyaMoveCommand):
    key = "东北"
    aliases = ["northeast", "ne"]

class CmdNorthwest(XianyaMoveCommand):
    key = "西北"
    aliases = ["northwest", "nw"]

class CmdSoutheast(XianyaMoveCommand):
    key = "东南"
    aliases = ["southeast", "se"]

class CmdSouthwest(XianyaMoveCommand):
    key = "西南"
    aliases = ["southwest", "sw"]

class CmdUp(XianyaMoveCommand):
    key = "上"
    aliases = ["up", "u"]

class CmdDown(XianyaMoveCommand):
    key = "下"
    aliases = ["down", "d"]

class CmdIn(XianyaMoveCommand):
    key = "里"
    aliases = ["in", "inside"]

class CmdOut(XianyaMoveCommand):
    key = "外"
    aliases = ["out", "outside"]
