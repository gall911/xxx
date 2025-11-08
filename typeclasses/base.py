"""
基础类型类

包含所有游戏对象的共同功能
"""

from evennia import DefaultObject
from utils.theme_hooks import apply_theme_to_object

class ObjectParent(DefaultObject):
    """
    所有游戏对象的父类
    
    这个类提供所有游戏对象共享的功能，包括主题应用
    """
    
    def at_object_creation(self):
        """
        当对象被创建时调用
        """
        super().at_object_creation()
        # 应用当前主题到新创建的对象
        apply_theme_to_object(self)
