"""
配置管理命令
"""

from evennia import Command, default_cmds
from utils.config_manager import game_config

class CmdConfig(default_cmds.MuxCommand):
    """
    配置管理命令

    用法:
      config reload <配置名> - 重新加载指定配置
      config list [配置名] - 列出配置或配置版本
      config validate <配置名> - 验证配置
      config save <配置名> [描述] - 保存当前配置为新版本
      config restore <配置名> <版本ID> - 恢复配置到指定版本
      config compare <配置名> <版本ID1> <版本ID2> - 比较两个配置版本
    """

    key = "config"
    locks = "cmd:perm(Admin)"
    help_category = "系统"

    def func(self):
        """实现配置管理功能"""
        if not self.args:
            self.msg("用法: config reload|list|validate|save|restore|compare [...]")
            return

        # 解析命令
        args = self.args.strip().split()
        action = args[0].lower()

        if action == "reload":
            if len(args) < 2:
                self.msg("用法: config reload <配置名>")
                return

            config_name = args[1]
            try:
                game_config.reload_config(config_name)
                self.msg(f"配置 {config_name} 已重新加载")
            except Exception as e:
                self.msg(f"重新加载配置失败: {e}")

        elif action == "list":
            if len(args) < 2:
                # 列出所有配置
                self.msg("可用配置: basic/attributes, basic/realms, systems/combat, items/weapons, items/armors, npcs/merchants")
                return

            config_name = args[1]
            try:
                versions = game_config.list_config_versions(config_name)
                if not versions:
                    self.msg(f"配置 {config_name} 没有版本记录")
                    return

                self.msg(f"配置 {config_name} 的版本列表:")
                for version in versions:
                    self.msg(f"  版本 {version['version_id']}: {version['description']} ({version['datetime']})")
            except Exception as e:
                self.msg(f"获取版本列表失败: {e}")

        elif action == "save":
            if len(args) < 2:
                self.msg("用法: config save <配置名> [描述]")
                return

            config_name = args[1]
            description = " ".join(args[2:]) if len(args) > 2 else "手动保存的版本"
            try:
                # 获取当前配置
                config_data = game_config.get_config(config_name)
                
                # 保存版本
                if game_config._instance._config_loader.enable_version_control and game_config._instance._config_loader.version_manager:
                    game_config._instance._config_loader.version_manager.save_version(
                        config_name, 
                        config_data, 
                        description
                    )
                    self.msg(f"配置 {config_name} 已保存为新版本: {description}")
                else:
                    self.msg("版本控制功能未启用")
            except Exception as e:
                self.msg(f"保存配置版本失败: {e}")

        elif action == "validate":
            if len(args) < 2:
                self.msg("用法: config validate <配置名>")
                return

            config_name = args[1]
            try:
                errors = game_config.validate_config(config_name)
                if not errors:
                    self.msg(f"配置 {config_name} 验证通过")
                else:
                    self.msg(f"配置 {config_name} 验证失败:")
                    for error in errors:
                        self.msg(f"  - {error}")
            except Exception as e:
                self.msg(f"验证配置失败: {e}")

        elif action == "restore":
            if len(args) < 3:
                self.msg("用法: config restore <配置名> <版本ID>")
                return

            config_name = args[1]
            version_id = args[2]
            try:
                game_config.restore_config_version(config_name, version_id)
                self.msg(f"配置 {config_name} 已恢复到版本 {version_id}")
            except Exception as e:
                self.msg(f"恢复配置版本失败: {e}")

        elif action == "compare":
            if len(args) < 4:
                self.msg("用法: config compare <配置名> <版本ID1> <版本ID2>")
                return

            config_name = args[1]
            version_id1 = args[2]
            version_id2 = args[3]
            try:
                diff = game_config.compare_config_versions(config_name, version_id1, version_id2)
                self.msg(f"配置 {config_name} 版本 {version_id1} 和 {version_id2} 的差异:")
                for change in diff["differences"]:
                    self.msg(f"  {change['path']}: {change['type']}")
            except Exception as e:
                self.msg(f"比较配置版本失败: {e}")

        else:
            self.msg("未知操作: " + action)
