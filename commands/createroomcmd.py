"""
创建房间命令

使用方法:
    dig <房间名>
"""

from evennia import default_cmds
from evennia import create_object
from utils.theme_utils import color_room_name, color_exit_name

class CmdDig(default_cmds.CmdDig):
    """
    创建房间
    
    使用方法:
        dig <房间名>
    """
    
    key = "dig"
    
    def func(self):
        """执行命令"""
        if not self.args:
            self.caller.msg("用法: dig <房间名>")
            return
            
        room_name = self.args
        
        # 创建新房间
        new_room = create_object("typeclasses.rooms.Room", key=room_name)
        new_room.db.desc = f"这是新创建的房间: {color_room_name(room_name)}"
        
        # 创建返回出口
        back_exit = create_object("typeclasses.exits.Exit", key="back")
        back_exit.destination = self.caller.location
        back_exit.db.desc = f"返回{color_room_name(self.caller.location.key)}的出口"
        
        # 创建前往新房间的出口
        to_exit = create_object("typeclasses.exits.Exit", key=room_name)
        to_exit.destination = new_room
        to_exit.db.desc = f"前往{color_room_name(room_name)}的出口"
        
        # 将出口添加到相应位置
        self.caller.location.exits.add(to_exit)
        new_room.exits.add(back_exit)
        
        self.caller.msg(f"已创建房间: {color_room_name(room_name)}")
        self.caller.msg(f"已创建出口: {color_exit_name(room_name)} 和 {color_exit_name('back')}")
