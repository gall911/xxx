from evennia import DefaultScript

class MurenRebuildScript(DefaultScript):
    """
    木人桩重建脚本 - 在木人桩被摧毁后重建它
    """

    def at_script_creation(self):
        """创建脚本时的初始化"""
        self.key = "muren_rebuild_script"
        self.desc = "木人桩重建脚本"
        self.interval = 5  # 5秒后重建
        self.persistent = True
        self.repeats = 1  # 只执行一次
        self.start_delay = True  # 启动后延迟一段时间再开始

    def at_start(self):
        """脚本启动时执行"""
        # 显示即将重建的消息
        if hasattr(self.db, 'muren_to_rebuild') and self.db.muren_to_rebuild:
            muren = self.db.muren_to_rebuild
            rebuild_start_message = getattr(muren.db, 'rebuild_start_message', 
                                           f"{muren.key}的碎片开始聚集，似乎要重新组合...")
            muren.location.msg_contents(rebuild_start_message.replace("{name}", muren.key))

    def at_repeat(self):
        """脚本执行时重建木人桩"""
        if hasattr(self.db, 'muren_to_rebuild') and self.db.muren_to_rebuild:
            muren = self.db.muren_to_rebuild
            muren.rebuild()
