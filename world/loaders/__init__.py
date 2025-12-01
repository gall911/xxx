# world/loaders/__init__.py
#"""加载器模块入口"""
from .game_data import CONFIG, GAME_DATA, get_config, get_data
from .config_loader import load_all_configs
from .data_loader import load_all_data
from .validator import validate_all_data
__all__ = [
    'CONFIG',
    'GAME_DATA',
    'get_config',
    'get_data',
    'load_all_configs',
    'load_all_data',
    'validate_all_data'
]