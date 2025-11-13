"""
配置更新回调函数

这个模块定义了配置系统更新时的回调函数。
"""

def on_attributes_updated(config_name, config_content):
    """
    属性配置更新回调

    当属性配置更新时，这个函数会被调用
    """
    # 这里可以添加配置更新后的处理逻辑
    # 例如，通知所有在线玩家属性已更新
    # from evennia import search_player  # 注释掉，因为此函数可能不存在
    from evennia.utils import logger

    # 记录日志
    logger.log_info(f"属性配置 {config_name} 已更新")

    # 通知所有在线玩家
    # for player in search_player("*"):
    #     if player.is_connected:
    #         player.msg("游戏属性已更新，部分效果可能需要重新登录才能生效。")

def on_realms_updated(config_name, config_content):
    """
    境界配置更新回调

    当境界配置更新时，这个函数会被调用
    """
    from evennia.utils import logger

    # 记录日志
    logger.log_info(f"境界配置 {config_name} 已更新")

def register_all_callbacks(config_manager):
    """
    注册所有配置更新回调

    Args:
        config_manager: 配置管理器实例
    """
    # 创建一个包装函数，用于过滤特定配置的更新
    def attributes_wrapper(config_name, config_content):
        if config_name == "basic/attributes":
            on_attributes_updated(config_name, config_content)
    
    def realms_wrapper(config_name, config_content):
        if config_name == "basic/realms":
            on_realms_updated(config_name, config_content)
    
    config_manager.register_update_callback(attributes_wrapper)
    config_manager.register_update_callback(realms_wrapper)
