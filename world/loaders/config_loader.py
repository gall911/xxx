# world/loaders/config_loader.py
"""游戏配置加载器"""
import yaml
from pathlib import Path
from evennia.utils import logger
from .game_data import CONFIG

def load_all_configs():
    """
    加载所有配置文件
    从 data/configs/ 目录加载所有 .yaml 文件
    """
    config_dir = Path('data/configs')
    
    if not config_dir.exists():
        logger.log_warn(f"配置目录不存在: {config_dir}")
        config_dir.mkdir(parents=True, exist_ok=True)
        return
    
    loaded_count = 0
    
    for yaml_file in config_dir.glob('*.yaml'):
        try:
            # 文件名作为配置key（去掉_settings后缀）
            config_key = yaml_file.stem.replace('_settings', '')
            
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
                # 支持两种格式：
                # 1. combat: {...}  (推荐)
                # 2. 直接 {...}
                if config_key in data:
                    CONFIG[config_key] = data[config_key]
                else:
                    CONFIG[config_key] = data
                
                loaded_count += 1
                logger.log_info(f"[配置] 已加载: {yaml_file.name}")
                
        except Exception as e:
            logger.log_err(f"[配置] 加载失败 {yaml_file.name}: {e}")
    
    logger.log_info(f"[配置] 总计加载 {loaded_count} 个配置文件")
    
    # 打印配置摘要
    if CONFIG.get('game'):
        logger.log_info(f"[配置] 游戏名称: {CONFIG['game'].get('name', '未设置')}")