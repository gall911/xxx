"""
快速创建房间命令

使用方法:
    digg <房间名>
"""

from evennia import Command
from evennia import create_object
from utils.theme_utils import color_room_name, color_exit_name

class CmdQuickDig(Command):
    """
    快速创建房间命令
    
    使用方法:
        quickdig <房间名>
    """
    
    key = "digg"
    help_category = "建造"
    
    # 在这里修改房间属性
    # 您可以根据需要修改这些默认值
    
    # 房间类型
    ROOM_TYPE = "normal"  # 可以是: normal, cave, mountain, water, indoor, outdoor
    
    # 是否为室内
    IS_INDOOR = False
    
    # 房间描述模板
    # 使用 {name} 作为房间名的占位符
    ROOM_DESC_TEMPLATE = """这是一个新创建的房间，名为{name}。

这里宽敞明亮，充满了神秘的气息。
四周的墙壁上似乎刻着一些古老的文字，但已经模糊不清。
空气中弥漫着淡淡的香味，让人感到心旷神怡。

{exits_hint}"""
    
    # 出口提示文本
    EXITS_HINT = "这里似乎有通向未知方向的出口。"
    
    # 返回出口描述模板
    # 使用 {from} 作为源房间名的占位符
    BACK_EXIT_DESC_TEMPLATE = "通往{from}的出口。"
    
    # 前往出口描述模板
    # 使用 {to} 作为目标房间名的占位符
    TO_EXIT_DESC_TEMPLATE = "通往{to}的出口。"
    
    def func(self):
        """执行命令"""
        if not self.args:
            self.caller.msg("用法: digg <房间名>")
            return
            
        room_name = self.args.strip()
        
        # 创建新房间
        new_room = create_object("typeclasses.rooms.Room", key=room_name)
        
        # 设置房间属性
        new_room.db.room_type = self.ROOM_TYPE
        new_room.db.is_indoor = self.IS_INDOOR
        
        # 设置房间描述
        exits_hint = self.EXITS_HINT if self.ROOM_TYPE == "normal" else ""
        room_desc = self.ROOM_DESC_TEMPLATE.format(
            name=color_room_name(room_name),
            exits_hint=exits_hint
        )
        new_room.db.desc = room_desc
        
        # 创建返回出口
        back_exit = create_object("typeclasses.exits.Exit", key="back")
        back_exit.destination = self.caller.location
        back_desc = self.BACK_EXIT_DESC_TEMPLATE.format(
            from=color_room_name(self.caller.location.key)
        )
        back_exit.db.desc = back_desc
        
        # 创建前往新房间的出口
        to_exit = create_object("typeclasses.exits.Exit", key=room_name)
        to_exit.destination = new_room
        to_desc = self.TO_EXIT_DESC_TEMPLATE.format(
            to=color_room_name(room_name)
        )
        to_exit.db.desc = to_desc
        
        # 将出口添加到相应位置
        self.caller.location.exits.add(to_exit)
        new_room.exits.add(back_exit)
        
        self.caller.msg(f"已创建房间: {color_room_name(room_name)}")
        self.caller.msg(f"已创建出口: {color_exit_name(room_name)} 和 {color_exit_name('back')}")
        self.caller.msg(f"房间类型: {self.ROOM_TYPE}, 室内: {self.IS_INDOOR}")
