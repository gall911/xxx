"""
重载命令集命令

使用方法:
    reload_cmds
"""

from evennia import Command

class CmdReloadCmds(Command):
    """
    重载命令集命令
    
    使用方法:
        reload_cmds
    """
    
    key = "reload_cmds"
    help_category = "系统"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        # 获取当前角色
        if not hasattr(caller, "cmdset"):
            caller.msg("无法重载命令集。")
            return
            
        # 清除并重新加载命令集
        caller.cmdset.remove("DefaultCharacter")
        caller.cmdset.add_default("commands.default_cmdsets.CharacterCmdSet")
        
        caller.msg("命令集已重载。")
