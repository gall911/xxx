"""
Characters
"""

from evennia.objects.objects import DefaultCharacter
from .objects import ObjectParent
from world.templates.loader import TemplateLoader

class Character(DefaultCharacter, ObjectParent):
    """
    Character typeclass.
    """
    def at_object_creation(self):
        """
        角色第一次创建时调用（只执行1次）
        用 base.yaml 初始化属性
        """
        TemplateLoader.apply_to_character(self, "base")