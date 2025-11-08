"""
移动消息模块

提供修仙风格的移动消息，根据房间属性显示不同描述
"""

# 默认的移动消息
DEFAULT_LEAVE_MSG = "{object}化作一道流光，自{origin}消逝。"
DEFAULT_ARRIVE_MSG = "{object}驾云而至，降临{destination}。"

# 室内移动消息
INDOOR_LEAVE_MSG = "{object}身影一闪，自{origin}中消失。"
INDOOR_ARRIVE_MSG = "{object}凭空出现，步入{destination}。"

# 室外移动消息
OUTDOOR_LEAVE_MSG = "{object}脚踏祥云，自{origin}飞升，向{destination}而去。"
OUTDOOR_ARRIVE_MSG = "{object}自九天而降，仙影显现于{destination}。"

# 特殊场景移动消息
CAVE_LEAVE_MSG = "{object}仙光一闪，离开了{origin}。"
CAVE_ARRIVE_MSG = "{object}踏云而来，进入{destination}。"

MOUNTAIN_LEAVE_MSG = "{object}御风而行，自{origin}飞升。"
MOUNTAIN_ARRIVE_MSG = "{object}自云端降落，现身于{destination}。"

WATER_LEAVE_MSG = "{object}踏浪而去，身影消失于{origin}。"
WATER_ARRIVE_MSG = "{object}御水而来，降临{destination}。"


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
    # 默认消息
    leave_msg = DEFAULT_LEAVE_MSG.format(object=object_name, origin=origin_name, destination=destination_name)
    arrive_msg = DEFAULT_ARRIVE_MSG.format(object=object_name, origin=origin_name, destination=destination_name)
    
    # 根据起始位置类型选择离开消息
    if origin_type:
        if origin_type.lower() == "cave":
            leave_msg = CAVE_LEAVE_MSG.format(object=object_name, origin=origin_name, destination=destination_name)
        elif origin_type.lower() == "mountain":
            leave_msg = MOUNTAIN_LEAVE_MSG.format(object=object_name, origin=origin_name, destination=destination_name)
        elif origin_type.lower() == "water":
            leave_msg = WATER_LEAVE_MSG.format(object=object_name, origin=origin_name, destination=destination_name)
        elif is_indoor is True:
            leave_msg = INDOOR_LEAVE_MSG.format(object=object_name, origin=origin_name, destination=destination_name)
        elif is_indoor is False:
            leave_msg = OUTDOOR_LEAVE_MSG.format(object=object_name, origin=origin_name, destination=destination_name)
    
    # 根据目标位置类型选择到达消息
    if dest_type:
        if dest_type.lower() == "cave":
            arrive_msg = CAVE_ARRIVE_MSG.format(object=object_name, origin=origin_name, destination=destination_name)
        elif dest_type.lower() == "mountain":
            arrive_msg = MOUNTAIN_ARRIVE_MSG.format(object=object_name, origin=origin_name, destination=destination_name)
        elif dest_type.lower() == "water":
            arrive_msg = WATER_ARRIVE_MSG.format(object=object_name, origin=origin_name, destination=destination_name)
        elif is_indoor is True:
            arrive_msg = INDOOR_ARRIVE_MSG.format(object=object_name, origin=origin_name, destination=destination_name)
        elif is_indoor is False:
            arrive_msg = OUTDOOR_ARRIVE_MSG.format(object=object_name, origin=origin_name, destination=destination_name)
    
    return leave_msg, arrive_msg
