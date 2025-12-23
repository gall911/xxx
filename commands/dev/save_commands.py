# commands/dev/save_commands.py
"""
存档管理命令 (开发者用)
"""
from evennia import Command


class CmdSave(Command):
    """
    手动保存角色数据
    
    用法:
      save [目标]
      
    不指定目标则保存自己
    """
    key = "save"
    aliases = ["存档"]
    locks = "cmd:all()"
    help_category = "通用"
    
    def func(self):
        from world.systems.save_system import SaveSystem
        
        if self.args:
            # 管理员可以保存其他人
            if not self.caller.check_permstring("Builder"):
                self.caller.msg("你只能保存自己的数据")
                return
            
            target = self.caller.search(self.args.strip())
            if not target:
                return
        else:
            target = self.caller
        
        if SaveSystem.save_character(target):
            self.caller.msg(f"|g{target.key} 的数据已保存！|n")
        else:
            self.caller.msg(f"|r保存失败|n")


class CmdSaveAll(Command):
    """
    保存所有在线角色
    
    用法:
      saveall
    """
    key = "saveall"
    aliases = ["全员存档"]
    locks = "cmd:perm(Builder)"
    help_category = "开发"
    
    def func(self):
        from world.systems.save_system import SaveSystem
        
        self.caller.msg("|y正在保存所有在线角色...|n")
        
        success, total = SaveSystem.save_all_online()
        
        self.caller.msg(f"|g已保存 {success}/{total} 个角色|n")


class CmdSaveConfig(Command):
    """
    查看/修改存档配置
    
    用法:
      saveconfig              # 查看当前配置
      saveconfig interval 600 # 设置间隔为10分钟
      saveconfig enable       # 启用自动存档
      saveconfig disable      # 禁用自动存档
    """
    key = "saveconfig"
    aliases = ["存档配置"]
    locks = "cmd:perm(Builder)"
    help_category = "开发"
    
    def func(self):
        from world.loaders.game_data import get_config, CONFIG
        
        if not self.args:
            # 显示当前配置
            self._show_config()
            return
        
        args = self.args.split()
        
        if args[0] == "interval":
            # 修改存档间隔
            if len(args) < 2:
                self.caller.msg("用法: saveconfig interval <秒数>")
                return
            
            try:
                interval = int(args[1])
                if interval < 60:
                    self.caller.msg("间隔不能小于60秒")
                    return
                
                # 修改配置
                CONFIG['game']['save_system']['auto_save_interval'] = interval
                
                # 重启自动存档
                from world.systems.save_system import stop_auto_save, start_auto_save
                stop_auto_save()
                start_auto_save()
                
                self.caller.msg(f"|g存档间隔已设置为 {interval} 秒|n")
                
            except ValueError:
                self.caller.msg("间隔必须是整数")
        
        elif args[0] == "enable":
            # 启用自动存档
            CONFIG['game']['save_system']['auto_save_enabled'] = True
            
            from world.systems.save_system import start_auto_save
            start_auto_save()
            
            self.caller.msg("|g自动存档已启用|n")
        
        elif args[0] == "disable":
            # 禁用自动存档
            CONFIG['game']['save_system']['auto_save_enabled'] = False
            
            from world.systems.save_system import stop_auto_save
            stop_auto_save()
            
            self.caller.msg("|y自动存档已禁用|n")
        
        else:
            self.caller.msg(f"未知选项: {args[0]}")
    
    def _show_config(self):
        """显示当前配置"""
        from world.loaders.game_data import get_config
        
        enabled = get_config('game.save_system.auto_save_enabled', True)
        interval = get_config('game.save_system.auto_save_interval', 300)
        
        quest = get_config('game.save_system.save_on_quest_complete', True)
        logout = get_config('game.save_system.save_on_logout', True)
        shutdown = get_config('game.save_system.save_on_shutdown', True)
        combat = get_config('game.save_system.save_on_combat_end', False)
        levelup = get_config('game.save_system.save_on_level_up', False)
        
        log_enabled = get_config('game.save_system.save_log_enabled', True)
        log_detail = get_config('game.save_system.save_log_detail', False)
        
        self.caller.msg("|c" + "=" * 50)
        self.caller.msg("存档系统配置")
        self.caller.msg("=" * 50 + "|n")
        
        self.caller.msg(f"\n自动存档: {'|g启用|n' if enabled else '|r禁用|n'}")
        self.caller.msg(f"存档间隔: |y{interval}|n 秒 ({interval//60} 分钟)")
        
        self.caller.msg("\n触发条件:")
        self.caller.msg(f"  任务完成: {'|g✓|n' if quest else '|r✗|n'}")
        self.caller.msg(f"  玩家下线: {'|g✓|n' if logout else '|r✗|n'}")
        self.caller.msg(f"  服务器关闭: {'|g✓|n' if shutdown else '|r✗|n'}")
        self.caller.msg(f"  战斗结束: {'|g✓|n' if combat else '|r✗|n'}")
        self.caller.msg(f"  升级时: {'|g✓|n' if levelup else '|r✗|n'}")
        
        self.caller.msg("\n日志:")
        self.caller.msg(f"  记录存档: {'|g✓|n' if log_enabled else '|r✗|n'}")
        self.caller.msg(f"  详细信息: {'|g✓|n' if log_detail else '|r✗|n'}")
        
        self.caller.msg("\n|c" + "=" * 50 + "|n")