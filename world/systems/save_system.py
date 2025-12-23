# world/systems/save_system.py
"""
角色存档系统
支持: 自动存档、手动存档、配置化开关
"""

from world.loaders.game_data import get_config
from evennia.utils import logger


class SaveSystem:
    """存档系统管理器"""
    
    @staticmethod
    def save_character(character):
        """
        保存单个角色数据
        
        Args:
            character: 角色对象
        
        Returns:
            bool: 是否保存成功
        """
        if not hasattr(character, '_save_to_db'):
            logger.log_err(f"[存档] {character.key} 没有 _save_to_db 方法")
            return False
        
        try:
            character._save_to_db()
            
            # 记录日志
            if get_config('game.save_system.save_log_enabled', True):
                detail = get_config('game.save_system.save_log_detail', False)
                
                if detail:
                    logger.log_info(
                        f"[存档] {character.key} - "
                        f"境界:{character.ndb.realm} "
                        f"等级:{character.ndb.level} "
                        f"经验:{character.ndb.exp}"
                    )
                else:
                    logger.log_info(f"[存档] {character.key}")
            
            return True
            
        except Exception as e:
            logger.log_err(f"[存档失败] {character.key}: {e}")
            return False
    
    @staticmethod
    def save_all_online():
        """
        保存所有在线角色
        
        Returns:
            tuple: (成功数, 总数)
        """
        from evennia import search_object
        
        # 获取所有在线角色
        characters = search_object(typeclass="typeclasses.characters.Character")
        
        success_count = 0
        total_count = 0
        
        for char in characters:
            # 检查是否在线
            if char.sessions.all():
                total_count += 1
                if SaveSystem.save_character(char):
                    success_count += 1
        
        if total_count > 0:
            logger.log_info(f"[批量存档] {success_count}/{total_count} 个角色")
        
        return success_count, total_count
    
    @staticmethod
    def should_save_on_event(event_type):
        """
        检查某个事件是否应该触发存档
        
        Args:
            event_type: 事件类型 ('quest_complete', 'combat_end', 'level_up')
        
        Returns:
            bool: 是否应该存档
        """
        config_map = {
            'quest_complete': 'game.save_system.save_on_quest_complete',
            'combat_end': 'game.save_system.save_on_combat_end',
            'level_up': 'game.save_system.save_on_level_up',
            'logout': 'game.save_system.save_on_logout',
            'shutdown': 'game.save_system.save_on_shutdown',
        }
        
        config_key = config_map.get(event_type)
        if not config_key:
            return False
        
        return get_config(config_key, True)


# ============================================
# 自动存档 Ticker (服务器启动时注册)
# ============================================

def auto_save_tick(*args, **kwargs):
    """自动存档回调函数"""
    # 检查是否启用
    if not get_config('game.save_system.auto_save_enabled', True):
        return
    
    SaveSystem.save_all_online()


def start_auto_save():
    """启动自动存档"""
    from evennia import TICKER_HANDLER
    
    # 检查是否启用
    if not get_config('game.save_system.auto_save_enabled', True):
        logger.log_info("[存档系统] 自动存档已禁用")
        return
    
    # 获取存档间隔
    interval = get_config('game.save_system.auto_save_interval', 300)
    
    # 注册 Ticker
    TICKER_HANDLER.add(
        interval=interval,
        callback=auto_save_tick,
        idstring="auto_save_characters",
        persistent=True
    )
    
    logger.log_info(f"[存档系统] 自动存档已启动，间隔 {interval} 秒")


def stop_auto_save():
    """停止自动存档"""
    from evennia import TICKER_HANDLER
    
    TICKER_HANDLER.remove(
        interval=None,
        callback=auto_save_tick,
        idstring="auto_save_characters"
    )
    
    logger.log_info("[存档系统] 自动存档已停止")