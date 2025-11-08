"""
修复出口别名的脚本

这个脚本会遍历所有出口，并为它们添加方向别名
"""

from evennia import create_script
from evennia.utils.search import search_object
from typeclasses.exits import Exit

def fix_exit_aliases():
    """
    修复所有出口的别名
    """
    # 获取所有出口
    exits = search_object("", typeclass=typeclasses.exits.Exit)
    
    print(f"找到 {len(exits)} 个出口")
    
    for exit in exits:
        print(f"处理出口: {exit.key} (#{exit.id})")
        # 获取出口的当前别名
        current_aliases = exit.aliases.all()
        print(f"当前别名: {current_aliases}")
        
        # 设置方向别名
        exit._setup_direction_aliases()
        
        # 获取更新后的别名
        new_aliases = exit.aliases.all()
        print(f"更新后别名: {new_aliases}")
        
        # 保存出口
        exit.save()
        print(f"已保存出口: {exit.key} (#{exit.id})")

if __name__ == "__main__":
    fix_exit_aliases()
