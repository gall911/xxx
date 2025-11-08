"""
LS命令 - 用于查看房间、出口和账号的命令集合（管理员命令）
"""

from evennia import default_cmds
from typeclasses.rooms import Room
from typeclasses.exits import Exit
from typeclasses.accounts import Account


class CmdLs(default_cmds.MuxCommand):
    """
    XX命令 - 用于列出房间、出口和账号（管理员命令）

    用法:
      xx r - 列出所有房间
      xx e - 列出所有出口
      xx a - 列出所有账号
    """
    key = "xx"
    locks = "cmd:perm(Builder)"

    def get_typeclass_path(self, obj):
        """获取对象的类型类路径"""
        # 尝试使用 typeclass_path 属性
        if hasattr(obj, 'typeclass_path') and obj.typeclass_path:
            return obj.typeclass_path
        # 否则使用类型信息构建路径
        return f"{type(obj).__module__}.{type(obj).__name__}"

    def list_rooms(self):
        """列出所有房间"""
        rooms = Room.objects.all()
        if not rooms:
            self.caller.msg("没有找到任何房间。")
            return

        # 列出每个房间
        for room in rooms:
            room_id = f"#{room.id}"
            room_name = room.key
            typeclass = self.get_typeclass_path(room)
            
            # 创建黄色可点击的房间名链接（点击移动到该房间）
            # |lc命令|lt显示文本|le 是Evennia的链接格式
            # |Y 是黄色，|n 是重置颜色
            # 使用 @teleport 命令传送到房间
            clickable_name = f"|lc@teleport {room_id}|lt|Y{room_name}|le|n"
            
            self.caller.msg(f"{room_id:8} {clickable_name} {typeclass}")

        self.caller.msg(f"总共找到 {len(rooms)} 个房间。")

    def list_exits(self):
        """列出所有出口"""
        exits = Exit.objects.all()
        if not exits:
            self.caller.msg("没有找到任何出口。")
            return

        # 列出每个出口
        for exit_obj in exits:
            exit_id = f"#{exit_obj.id}"
            exit_name = exit_obj.key
            typeclass = self.get_typeclass_path(exit_obj)
            
            self.caller.msg(f"{exit_id:8} {exit_name:40} {typeclass}")

        self.caller.msg(f"总共找到 {len(exits)} 个出口。")

    def list_accounts(self):
        """列出所有账号"""
        accounts = Account.objects.all()
        if not accounts:
            self.caller.msg("没有找到任何账号。")
            return

        # 列出每个账号
        for account in accounts:
            account_id = f"#{account.id}"
            account_name = account.key
            typeclass = self.get_typeclass_path(account)
            
            self.caller.msg(f"{account_id:8} {account_name:40} {typeclass}")

        self.caller.msg(f"总共找到 {len(accounts)} 个账号。")

    def func(self):
        """
        执行命令
        """
        if not self.args:
            self.caller.msg("用法: xx r/e/a (r=房间, e=出口, a=账号)")
            return

        arg = self.args.strip().lower()
        if arg == "r" or arg == "room":
            self.list_rooms()
        elif arg == "e" or arg == "exit":
            self.list_exits()
        elif arg == "a" or arg == "account":
            self.list_accounts()
        else:
            self.caller.msg(f"未知的参数 '{arg}'。用法: xx r/e/a (r=房间, e=出口, a=账号)")


class CmdLr(default_cmds.MuxCommand):
    """
    列出所有房间（简短别名）
    """
    key = "lr"
    locks = "cmd:perm(Builder)"
    
    def get_typeclass_path(self, obj):
        """获取对象的类型类路径"""
        if hasattr(obj, 'typeclass_path') and obj.typeclass_path:
            return obj.typeclass_path
        return f"{type(obj).__module__}.{type(obj).__name__}"
    
    def func(self):
        """列出所有房间"""
        rooms = Room.objects.all()
        if not rooms:
            self.caller.msg("没有找到任何房间。")
            return

        for room in rooms:
            room_id = f"#{room.id}"
            room_name = room.key
            typeclass = self.get_typeclass_path(room)
            clickable_name = f"|lc@teleport {room_id}|lt|Y{room_name}|le|n"
            self.caller.msg(f"{room_id:8} {clickable_name} {typeclass}")

        self.caller.msg(f"总共找到 {len(rooms)} 个房间。")


class CmdLe(default_cmds.MuxCommand):
    """
    列出所有出口（简短别名）
    """
    key = "le"
    locks = "cmd:perm(Builder)"
    
    def get_typeclass_path(self, obj):
        """获取对象的类型类路径"""
        if hasattr(obj, 'typeclass_path') and obj.typeclass_path:
            return obj.typeclass_path
        return f"{type(obj).__module__}.{type(obj).__name__}"
    
    def func(self):
        """列出所有出口"""
        exits = Exit.objects.all()
        if not exits:
            self.caller.msg("没有找到任何出口。")
            return

        for exit_obj in exits:
            exit_id = f"#{exit_obj.id}"
            exit_name = exit_obj.key
            typeclass = self.get_typeclass_path(exit_obj)
            self.caller.msg(f"{exit_id:8} {exit_name:40} {typeclass}")

        self.caller.msg(f"总共找到 {len(exits)} 个出口。")


class CmdLa(default_cmds.MuxCommand):
    """
    列出所有账号（简短别名）
    """
    key = "la"
    locks = "cmd:perm(Builder)"
    
    def get_typeclass_path(self, obj):
        """获取对象的类型类路径"""
        if hasattr(obj, 'typeclass_path') and obj.typeclass_path:
            return obj.typeclass_path
        return f"{type(obj).__module__}.{type(obj).__name__}"
    
    def func(self):
        """列出所有账号"""
        accounts = Account.objects.all()
        if not accounts:
            self.caller.msg("没有找到任何账号。")
            return

        for account in accounts:
            account_id = f"#{account.id}"
            account_name = account.key
            typeclass = self.get_typeclass_path(account)
            self.caller.msg(f"{account_id:8} {account_name:40} {typeclass}")

        self.caller.msg(f"总共找到 {len(accounts)} 个账号。")
