"""
测试出口搜索方法命令

使用方法: testexit
"""

from evennia import Command

class CmdTestExit(Command):
    """
    测试不同的出口搜索方法
    
    使用方法:
        testexit
    """
    
    key = "testexit"
    help_category = "系统"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        # 方法1：直接使用search_object_typeclass
        caller.msg("方法1：使用search_object_typeclass")
        try:
            from evennia.utils.search import search_object_typeclass
            exits = search_object_typeclass("typeclasses.exits.Exit")
            caller.msg(f"找到 {len(exits)} 个出口")
            for exit in exits:
                caller.msg(f"- {exit.key} (#{exit.id})")
        except Exception as e:
            caller.msg(f"错误: {e}")
        
        # 方法2：使用search_object和typeclass
        caller.msg("\n方法2：使用search_object和typeclass")
        try:
            from evennia.utils.search import search_object
            from typeclasses.exits import Exit
            exits = search_object("*", typeclass=Exit)
            caller.msg(f"找到 {len(exits)} 个出口")
            for exit in exits:
                caller.msg(f"- {exit.key} (#{exit.id})")
        except Exception as e:
            caller.msg(f"错误: {e}")
        
        # 方法3：使用search_object并筛选
        caller.msg("\n方法3：使用search_object并筛选")
        try:
            from evennia.utils.search import search_object
            all_objects = search_object("*")
            exits = [obj for obj in all_objects if hasattr(obj, "destination") and obj.destination]
            caller.msg(f"找到 {len(exits)} 个出口")
            for exit in exits:
                caller.msg(f"- {exit.key} (#{exit.id})")
        except Exception as e:
            caller.msg(f"错误: {e}")
        
        # 方法4：使用search_tag
        caller.msg("\n方法4：使用search_tag")
        try:
            from evennia.utils.search import search_tag
            exits = [obj for obj in search_tag(key="exit", category="object_type") if hasattr(obj, "destination") and obj.destination]
            caller.msg(f"找到 {len(exits)} 个出口")
            for exit in exits:
                caller.msg(f"- {exit.key} (#{exit.id})")
        except Exception as e:
            caller.msg(f"错误: {e}")
        
        # 方法5：直接查询数据库
        caller.msg("\n方法5：直接查询数据库")
        try:
            from evennia.utils.dbhandler import get_all_objs
            exits = [obj for obj in get_all_objs() if hasattr(obj, "destination") and obj.destination]
            caller.msg(f"找到 {len(exits)} 个出口")
            for exit in exits:
                caller.msg(f"- {exit.key} (#{exit.id})")
        except Exception as e:
            caller.msg(f"错误: {e}")
        
        # 方法6：使用默认的Exit类
        caller.msg("\n方法6：使用默认的Exit类")
        try:
            from evennia.utils.search import search_object_typeclass
            from evennia.objects.objects import DefaultExit
            exits = search_object_typeclass(DefaultExit)
            caller.msg(f"找到 {len(exits)} 个出口")
            for exit in exits:
                caller.msg(f"- {exit.key} (#{exit.id})")
        except Exception as e:
            caller.msg(f"错误: {e}")
