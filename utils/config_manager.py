"""
游戏配置管理器

这个模块提供了一个全局配置管理器，用于在MUD游戏中使用配置系统。
"""

import os
import sys

# 添加config_system到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_system import get_config_loader

class GameConfigManager:
    """
    游戏配置管理器

    提供全局配置访问和管理功能
    """

    _instance = None
    _config_loader = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._config_loader = get_config_loader(
                enable_validation=True,
                enable_version_control=False
            )
        return cls._instance

    @classmethod
    def get_config(cls, config_name):
        """获取配置"""
        return cls._instance._config_loader.get_config(config_name)

    @classmethod
    def reload_config(cls, config_name):
        """重新加载配置"""
        return cls._instance._config_loader.reload_config(config_name)

    @classmethod
    def register_update_callback(cls, callback):
        """注册配置更新回调"""
        return cls._instance._config_loader.register_update_callback(callback)

    @classmethod
    def validate_config(cls, config_name):
        """验证配置"""
        return cls._instance._config_loader.validate_config(config_name)

    @classmethod
    def list_config_versions(cls, config_name):
        """列出配置版本"""
        return cls._instance._config_loader.list_config_versions(config_name)

    @classmethod
    def restore_config_version(cls, config_name, version_id):
        """恢复配置版本"""
        return cls._instance._config_loader.restore_config_version(config_name, version_id)

    @classmethod
    def compare_config_versions(cls, config_name, version_id1, version_id2):
        """比较配置版本"""
        return cls._instance._config_loader.compare_config_versions(config_name, version_id1, version_id2)

    @classmethod
    def add_validation_rule(cls, config_name, key_path, rule_type, **kwargs):
        """添加验证规则"""
        return cls._instance._config_loader.add_validation_rule(config_name, key_path, rule_type, **kwargs)

# 创建全局配置管理器实例
game_config = GameConfigManager()

# 注册配置更新回调
from .config_callbacks import register_all_callbacks
register_all_callbacks(game_config)