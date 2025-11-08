"""
修复出口别名命令

使用方法: fixexit
"""

from evennia import Command
from typeclasses.exits import Exit
from evennia.utils.search import search_object

class CmdFixExit(Command):
    """
    修复所有出口的别名
    
    使用方法:
        fixexit
    """
    
    key = "fixexit"
    help_category = "系统"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        # 获取所有出口
        exits = Exit.objects.all()
        
        if not exits:
            caller.msg("没有找到任何出口。")
            return
            
        caller.msg(f"找到 {len(exits)} 个出口，开始修复别名...")
        
        fixed_count = 0
        for exit in exits:
            # 获取出口的当前别名
            current_aliases = exit.aliases.all()
            
            # 设置方向别名
            exit._setup_direction_aliases()
            
            # 获取更新后的别名
            new_aliases = exit.aliases.all()
            
            # 如果有变化，保存出口
            if current_aliases != new_aliases:
                exit.save()
                fixed_count += 1
                caller.msg(f"已修复出口: {exit.key} (#{exit.id}) - 别名: {new_aliases}")
        
        caller.msg(f"修复完成！共修复了 {fixed_count} 个出口的别名。")
