"""
主题钩子模块

提供主题系统与游戏对象的集成
"""

from evennia import ObjectDB
from server.conf.theme import CHARACTER_NAME, ACCOUNT_NAME, ROOM_NAME, EXIT_NAME
from utils.theme_utils import color_room_name, color_exit_name

def apply_theme_to_object(obj):
    """将当前主题应用到对象
    
    Args:
        obj: 要应用主题的对象
    """
    # 根据对象类型应用不同的主题设置
    if hasattr(obj, 'destination') and obj.destination:
        # 这是一个出口，存储带颜色的显示名称
        obj.db.display_name = f"{EXIT_NAME}{obj.key}|n"
    elif hasattr(obj, 'contents'):
        # 这是一个房间，存储带颜色的显示名称
        obj.db.display_name = f"{ROOM_NAME}{obj.key}|n"
    
    return obj

def apply_theme_to_all_objects():
    """将主题应用到所有现有对象"""
    
    # 应用到所有房间
    from typeclasses.rooms import Room
    rooms = Room.objects.all()
    for room in rooms:
        room.db.display_name = f"{ROOM_NAME}{room.key}|n"
    
    # 应用到所有出口
    from typeclasses.exits import Exit
    exits = Exit.objects.all()
    for exit in exits:
        exit.db.display_name = f"{EXIT_NAME}{exit.key}|n"
    
    return len(rooms) + len(exits)
