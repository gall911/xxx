"""
移动消息模块

提供修仙风格的移动消息，根据房间属性显示不同描述
"""

import random

from server.conf.theme import MOVE_IN, MOVE_OUT
# 默认的移动消息
DEFAULT_LEAVE_MSGS = [
    "{object}化作一道流光，自{origin}消逝。",
    "{object}掐动法诀，身形化作一缕青烟，自{origin}飘然而出。",
    "{object}袖袍一挥，空间微颤，自{origin}瞬间转移。",
    "{object}仙气缭绕，身影渐淡，自{origin}消散无形。"
]
DEFAULT_ARRIVE_MSGS = [
    "{object}驾云而至，降临{destination}。",
    "{object}自九天而降，仙影显现于{destination}。",
    "{object}踏云而来，进入{destination}。",
    "{object}凭空出现，步入{destination}。"
]

# 室内移动消息
INDOOR_LEAVE_MSGS = [
    "{object}身影一闪，自{origin}中消失。",
    "{object}掐动法诀，身形化作一缕青烟，自{origin}飘然而出。",
    "{object}袖袍一挥，空间微颤，自{origin}瞬间转移。",
    "{object}仙气缭绕，身影渐淡，自{origin}消散无形。"
]
INDOOR_ARRIVE_MSGS = [
    "{object}凭空出现，步入{destination}。",
    "{object}仙光一闪，出现在{destination}中。",
    "{object}道袍轻摆，步步生莲，自虚空中步入{destination}。",
    "{object}手捏法印，口诵真言，现身于{destination}。"
]

# 室外移动消息
OUTDOOR_LEAVE_MSGS = [
    "{object}脚踏祥云，自{origin}飞升，向{destination}而去。",
    "{object}御剑而起，自{origin}冲天而起，化作长虹直入云霄。",
    "{object}驾云而行，自{origin}缓缓升起，飘然而去。",
    "{object}袖袍鼓荡，自{origin}腾空而起，如飞仙般飘向远方。"
]
OUTDOOR_ARRIVE_MSGS = [
    "{object}自九天而降，仙影显现于{destination}。",
    "{object}踏云而来，降临{destination}。",
    "{object}御剑而落，剑光一闪，已至{destination}。",
    "{object}脚踏祥云，自云端缓缓降落，现身于{destination}。"
]

# 特殊场景移动消息
CAVE_LEAVE_MSGS = [
    "{object}仙光一闪，离开了{origin}。",
    "{object}掐诀念咒，身影消失在黑暗中。",
    "{object}化作一道流光，消失在洞穴深处。",
    "{object}手捏法印，身影融入阴影，消失不见。"
]
CAVE_ARRIVE_MSGS = [
    "{object}踏云而来，进入{destination}。",
    "{object}仙光一闪，出现在洞穴中。",
    "{object}自黑暗中现身，步入{destination}。",
    "{object}身影由虚转实，出现在{destination}中。"
]

MOUNTAIN_LEAVE_MSGS = [
    "{object}御风而行，自{origin}飞升。",
    "{object}脚踏祥云，自山巅冉冉升起。",
    "{object}化作一道流光，冲天而起。",
    "{object}袖袍鼓荡，乘风而去。"
]
MOUNTAIN_ARRIVE_MSGS = [
    "{object}自云端降落，现身于{destination}。",
    "{object}踏云而来，落在山巅。",
    "{object}御剑而落，现身于{destination}。",
    "{object}仙风道骨，自天而降，立于{destination}。"
]

WATER_LEAVE_MSGS = [
    "{object}踏浪而去，身影消失于{origin}。",
    "{object}御水而行，化作一道水光消失。",
    "{object}袖袍一挥，水面分开，身影消失其中。",
    "{object}足下生波，乘风破浪而去。"
]
WATER_ARRIVE_MSGS = [
    "{object}御水而来，降临{destination}。",
    "{object}自水中现身，步入{destination}。",
    "{object}踏浪而来，身影由虚转实。",
    "{object}水面分开，{object}从中走出，步入{destination}。"
]


def get_movement_message(object_name, origin_name, destination_name, is_indoor=None, origin_type=None, dest_type=None):
    """
    根据房间属性获取移动消息
    
    Args:
        object_name (str): 移动的对象名称
        origin_name (str): 起始位置名称
        destination_name (str): 目标位置名称
        is_indoor (bool, optional): 是否为室内。None表示未知
        origin_type (str, optional): 起始位置类型
        dest_type (str, optional): 目标位置类型
    
    Returns:
        tuple: (离开消息, 到达消息)
    """
    # 初始化消息列表
    leave_msgs = []
    arrive_msgs = []
    
    # 添加默认消息
    leave_msgs.extend(DEFAULT_LEAVE_MSGS)
    arrive_msgs.extend(DEFAULT_ARRIVE_MSGS)
    
    # 随机选择消息
    leave_msg = random.choice(leave_msgs).format(object=object_name, origin=origin_name, destination=destination_name)
    arrive_msg = random.choice(arrive_msgs).format(object=object_name, origin=origin_name, destination=destination_name)
    
    # 根据起始位置类型选择离开消息
    if origin_type:
        if origin_type.lower() == "cave":
            leave_msgs.extend(CAVE_LEAVE_MSGS)
        elif origin_type.lower() == "mountain":
            leave_msgs.extend(MOUNTAIN_LEAVE_MSGS)
        elif origin_type.lower() == "water":
            leave_msgs.extend(WATER_LEAVE_MSGS)
        elif is_indoor is True:
            leave_msgs.extend(INDOOR_LEAVE_MSGS)
        elif is_indoor is False:
            leave_msgs.extend(OUTDOOR_LEAVE_MSGS)
    
    # 根据目标位置类型选择到达消息
    if dest_type:
        if dest_type.lower() == "cave":
            arrive_msgs.extend(CAVE_ARRIVE_MSGS)
        elif dest_type.lower() == "mountain":
            arrive_msgs.extend(MOUNTAIN_ARRIVE_MSGS)
        elif dest_type.lower() == "water":
            arrive_msgs.extend(WATER_ARRIVE_MSGS)
        elif is_indoor is True:
            arrive_msgs.extend(INDOOR_ARRIVE_MSGS)
        elif is_indoor is False:
            arrive_msgs.extend(OUTDOOR_ARRIVE_MSGS)
     # 随机选择消息
    leave_template = random.choice(leave_msgs)
    arrive_template = random.choice(arrive_msgs)
    
    # 动态添加颜色到离开消息
    # 在对象名称后插入颜色代码
    leave_msg = leave_template.format(
    object=f"{object_name}|n{MOVE_OUT}",  # 角色名+移动颜色
    origin=f"{origin_name}|n{MOVE_OUT}",       # 起始房间+移动颜色
    destination=f"{destination_name}|n{MOVE_OUT}"  # 
    )
    
    # 动态添加颜色到到达消息
    # 在对象名称后插入颜色代码
    arrive_msg = arrive_template.format(
        object=f"{object_name}{MOVE_IN}",  # 将颜色添加到对象名后面
        origin=origin_name,
        destination=destination_name
    )
    
    return leave_msg, arrive_msg
    