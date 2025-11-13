
# 法术基类
from evennia.objects.objects import DefaultObject

class BaseSpell(DefaultObject):
    """
    所有法术的基类，定义了法术的基本属性和方法
    """

    def __init__(self, *args, **kwargs):
        """初始化法术对象"""
        super().__init__(*args, **kwargs)

    def cast(self, caster, target=None):
        """
        施放法术的通用方法，子类应该重写此方法

        Args:
            caster (Character): 施法者
            target (Character or None): 目标

        Returns:
            tuple: (success, message) - 是否成功及结果消息
        """
        # 默认实现，子类应该重写
        return False, "这个法术还没有实现。"

    def calculate_damage(self, caster, target):
        """
        计算实际伤害值的通用方法

        Args:
            caster (Character): 施法者
            target (Character): 目标

        Returns:
            int: 实际伤害值
        """
        # 默认实现，子类可以重写
        return self.damage

    def can_cast(self, caster):
        """
        检查施法者是否可以施放此法术

        Args:
            caster (Character): 施法者

        Returns:
            tuple: (can_cast, reason) - 是否可以施放及原因
        """
        # 检查法力值
        if caster.db.mana is not None and caster.db.mana < self.db.mana_cost:
            return False, f"法力不足，需要{self.db.mana_cost}点法力。"

        # 检查冷却时间
        if caster.db.spell_cooldowns is not None and self.db.key in caster.db.spell_cooldowns:
            remaining = caster.db.spell_cooldowns[self.db.key]
            return False, f"法术冷却中，还需{remaining}秒。"

        return True, "可以施放。"
