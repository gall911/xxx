"""
Server startstop hooks

This module contains functions called by Evennia at various
points during its startup, reload and shutdown sequence. It
allows for customizing the server operation as desired.

This module must contain at least these global functions:

at_server_init()
at_server_start()
at_server_stop()
at_server_reload_start()
at_server_reload_stop()
at_server_cold_start()
at_server_cold_stop()

"""

# server/conf/at_server_startstop.py
"""
服务器启动和停止时的钩子
"""

def at_server_start():
    """
    服务器每次启动时调用
    
    注意：这会在reload时也调用
    """
    from evennia.utils import logger
    
    logger.log_info("=" * 60)
    logger.log_info("服务器启动中...")
    logger.log_info("=" * 60)
    
    # 重新加载游戏数据
    logger.log_info("[启动] 加载配置...")
    from world.loaders.config_loader import load_all_configs
    load_all_configs()
    
    logger.log_info("[启动] 加载游戏数据...")
    from world.loaders.data_loader import load_all_data
    load_all_data()
    
    # 重新初始化战斗管理器
    logger.log_info("[启动] 初始化战斗管理器...")
    from world.managers.combat_manager import COMBAT_MANAGER
    
    # 清理所有战斗状态（服务器重启后）
    COMBAT_MANAGER.active_combats.clear()
    
    logger.log_info("[启动] 服务器已就绪")
    logger.log_info("=" * 60)


def at_server_stop():
    """
    服务器停止时调用
    """
    from evennia.utils import logger
    
    logger.log_info("=" * 60)
    logger.log_info("服务器正在关闭...")
    logger.log_info("=" * 60)
    
    # 停止所有战斗
    from world.managers.combat_manager import COMBAT_MANAGER
    
    for combat_id in list(COMBAT_MANAGER.active_combats.keys()):
        COMBAT_MANAGER._end_combat(combat_id, None)
    
    logger.log_info("[停止] 已清理所有战斗状态")
    logger.log_info("[停止] 服务器已安全关闭")
    logger.log_info("=" * 60)


def at_server_reload_start():
    """
    服务器reload开始时调用
    """
    from evennia.utils import logger
    logger.log_info("[重载] 服务器重载开始...")


def at_server_reload_stop():
    """
    服务器reload完成时调用
    """
    from evennia.utils import logger
    logger.log_info("[重载] 服务器重载完成")