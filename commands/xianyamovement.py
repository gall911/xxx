"""
仙侠风格移动命令修改

修改 Evennia 默认的移动命令，使其使用仙侠风格的描述
"""

from evennia import default_cmds
from world.movement_messages import get_movement_message

class CmdNorth(default_cmds.CmdNorth):
    """
    向北移动
    """
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        if not self.args:
            return
            
        # 检查是否有对应的出口
        exit_obj = caller.search("north", destination=caller.location)
        
        if not exit_obj:
            caller.msg("北方似乎有结界阻拦，无法通过。")
            return
            
        # 检查出口是否可用
        if not exit_obj.access(caller, "traverse"):
            caller.msg(f"无法通过向北的出口。")
            return
            
        # 获取源房间和目标房间
        source_room = caller.location
        target_room = exit_obj.destination
        
        # 获取房间类型
        origin_type = getattr(source_room.db, "room_type", None)
        dest_type = getattr(target_room.db, "room_type", None)
        
        # 获取房间室内/室外属性
        origin_is_indoor = getattr(source_room.db, "is_indoor", None)
        dest_is_indoor = getattr(target_room.db, "is_indoor", None)
        
        # 替换房间名（去掉编号）
        from_room_name = source_room.key.split('(')[0].strip()
        to_room_name = target_room.key.split('(')[0].strip()
        
        # 获取移动消息
        leave_msg, arrive_msg = get_movement_message(
            object_name=caller.key,
            origin_name=from_room_name,
            destination_name=to_room_name,
            is_indoor=origin_is_indoor,
            origin_type=origin_type,
            dest_type=dest_type
        )
        
        # 移动角色
        caller.msg(f"你{leave_msg}，{arrive_msg}")
        caller.move_to(target_room)
        
        # 检查是否在移动后需要显示房间描述
        caller.execute_cmd("look")

# 为其他方向创建类似的命令
class CmdSouth(default_cmds.CmdSouth):
    """向南移动"""
    
    def func(self):
        caller = self.caller
        
        exit_obj = caller.search("south", destination=caller.location)
        
        if not exit_obj:
            caller.msg("南方似乎有结界阻拦，无法通过。")
            return
            
        if not exit_obj.access(caller, "traverse"):
            caller.msg(f"无法通过向南的出口。")
            return
            
        source_room = caller.location
        target_room = exit_obj.destination
        
        origin_type = getattr(source_room.db, "room_type", None)
        dest_type = getattr(target_room.db, "room_type", None)
        
        origin_is_indoor = getattr(source_room.db, "is_indoor", None)
        dest_is_indoor = getattr(target_room.db, "is_indoor", None)
        
        from_room_name = source_room.key.split('(')[0].strip()
        to_room_name = target_room.key.split('(')[0].strip()
        
        leave_msg, arrive_msg = get_movement_message(
            object_name=caller.key,
            origin_name=from_room_name,
            destination_name=to_room_name,
            is_indoor=origin_is_indoor,
            origin_type=origin_type,
            dest_type=dest_type
        )
        
        caller.msg(f"你{leave_msg}，{arrive_msg}")
        caller.move_to(target_room)
        caller.execute_cmd("look")

class CmdEast(default_cmds.CmdEast):
    """向东移动"""
    
    def func(self):
        caller = self.caller
        
        exit_obj = caller.search("east", destination=caller.location)
        
        if not exit_obj:
            caller.msg("东方似乎有结界阻拦，无法通过。")
            return
            
        if not exit_obj.access(caller, "traverse"):
            caller.msg(f"无法通过向东的出口。")
            return
            
        source_room = caller.location
        target_room = exit_obj.destination
        
        origin_type = getattr(source_room.db, "room_type", None)
        dest_type = getattr(target_room.db, "room_type", None)
        
        origin_is_indoor = getattr(source_room.db, "is_indoor", None)
        dest_is_indoor = getattr(target_room.db, "is_indoor", None)
        
        from_room_name = source_room.key.split('(')[0].strip()
        to_room_name = target_room.key.split('(')[0].strip()
        
        leave_msg, arrive_msg = get_movement_message(
            object_name=caller.key,
            origin_name=from_room_name,
            destination_name=to_room_name,
            is_indoor=origin_is_indoor,
            origin_type=origin_type,
            dest_type=dest_type
        )
        
        caller.msg(f"你{leave_msg}，{arrive_msg}")
        caller.move_to(target_room)
        caller.execute_cmd("look")

class CmdWest(default_cmds.CmdWest):
    """向西移动"""
    
    def func(self):
        caller = self.caller
        
        exit_obj = caller.search("west", destination=caller.location)
        
        if not exit_obj:
            caller.msg("西方似乎有结界阻拦，无法通过。")
            return
            
        if not exit_obj.access(caller, "traverse"):
            caller.msg(f"无法通过向西的出口。")
            return
            
        source_room = caller.location
        target_room = exit_obj.destination
        
        origin_type = getattr(source_room.db, "room_type", None)
        dest_type = getattr(target_room.db, "room_type", None)
        
        origin_is_indoor = getattr(source_room.db, "is_indoor", None)
        dest_is_indoor = getattr(target_room.db, "is_indoor", None)
        
        from_room_name = source_room.key.split('(')[0].strip()
        to_room_name = target_room.key.split('(')[0].strip()
        
        leave_msg, arrive_msg = get_movement_message(
            object_name=caller.key,
            origin_name=from_room_name,
            destination_name=to_room_name,
            is_indoor=origin_is_indoor,
            origin_type=origin_type,
            dest_type=dest_type
        )
        
        caller.msg(f"你{leave_msg}，{arrive_msg}")
        caller.move_to(target_room)
        caller.execute_cmd("look")
