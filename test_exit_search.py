"""
测试出口搜索方法
"""

# 方法1：直接使用search_object_typeclass
print("方法1：使用search_object_typeclass")
try:
    from evennia.utils.search import search_object_typeclass
    exits = search_object_typeclass("typeclasses.exits.Exit")
    print(f"找到 {len(exits)} 个出口")
    for exit in exits:
        print(f"- {exit.key} (#{exit.id})")
except Exception as e:
    print(f"错误: {e}")

# 方法2：使用search_object和typeclass
print("\n方法2：使用search_object和typeclass")
try:
    from evennia.utils.search import search_object
    from typeclasses.exits import Exit
    exits = search_object("*", typeclass=Exit)
    print(f"找到 {len(exits)} 个出口")
    for exit in exits:
        print(f"- {exit.key} (#{exit.id})")
except Exception as e:
    print(f"错误: {e}")

# 方法3：使用search_object并筛选
print("\n方法3：使用search_object并筛选")
try:
    from evennia.utils.search import search_object
    all_objects = search_object("*")
    exits = [obj for obj in all_objects if hasattr(obj, "destination") and obj.destination]
    print(f"找到 {len(exits)} 个出口")
    for exit in exits:
        print(f"- {exit.key} (#{exit.id})")
except Exception as e:
    print(f"错误: {e}")

# 方法4：使用search_tag
print("\n方法4：使用search_tag")
try:
    from evennia.utils.search import search_tag
    exits = [obj for obj in search_tag(key="exit", category="object_type") if hasattr(obj, "destination") and obj.destination]
    print(f"找到 {len(exits)} 个出口")
    for exit in exits:
        print(f"- {exit.key} (#{exit.id})")
except Exception as e:
    print(f"错误: {e}")

# 方法5：直接查询数据库
print("\n方法5：直接查询数据库")
try:
    from evennia.utils.dbhandler import get_all_objs
    exits = [obj for obj in get_all_objs() if hasattr(obj, "destination") and obj.destination]
    print(f"找到 {len(exits)} 个出口")
    for exit in exits:
        print(f"- {exit.key} (#{exit.id})")
except Exception as e:
    print(f"错误: {e}")

# 方法6：使用默认的Exit类
print("\n方法6：使用默认的Exit类")
try:
    from evennia.utils.search import search_object_typeclass
    from evennia.objects.objects import DefaultExit
    exits = search_object_typeclass(DefaultExit)
    print(f"找到 {len(exits)} 个出口")
    for exit in exits:
        print(f"- {exit.key} (#{exit.id})")
except Exception as e:
    print(f"错误: {e}")
