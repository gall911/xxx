"""
自定义NPC类型类
"""

from typeclasses.characters import Character
from evennia.utils import logger

class NPC(Character):
    """
    自定义NPC类
    """
    def at_object_creation(self):
        """
        初始化NPC属性
        """
        super().at_object_creation()
        self.db.npc = True
        self.db.hp = 100
        self.db.max_hp = 100
        self.db.is_invincible = False  # 默认不是无敌的
        self.db.display_name = None  # 自定义显示名称
        
    def at_damage(self, damage, attacker=None):
        """
        当受到伤害时调用
        """
        if self.db.is_invincible:
            # 如果是无敌的，不减少HP
            self.msg("你的攻击对这个目标无效。")
            if attacker:
                attacker.msg(f"你的攻击对{self.key}无效。")
            return 0
        else:
            # 调用父类的伤害处理
            return super().at_damage(damage, attacker)
            
    def heal(self, amount):
        """
        治疗NPC
        """
        if not self.db.hp:
            self.db.hp = 0
        if not self.db.max_hp:
            self.db.max_hp = 100
            
        self.db.hp = min(self.db.max_hp, self.db.hp + amount)
        
    def set_invincible(self, state=True):
        """
        设置NPC为无敌状态
        """
        self.db.is_invincible = state
        if state:
            self.msg("你感到自己变得坚不可摧。")
        else:
            self.msg("你感到自己的力量恢复了正常。")
            
    def get_display_name(self, looker=None, **kwargs):
        """
        获取NPC的显示名称
        
        Args:
            looker: 查看者对象
            **kwargs: 其他参数
            
        Returns:
            str: NPC的显示名称
        """
        # 如果设置了自定义显示名称，使用它
        if self.db.display_name:
            return self.db.display_name
            
        # 否则使用默认名称格式
        # 检查是否有别名，如果有则显示为"名称（别名）"格式
        aliases = self.aliases.all()
        if aliases:
            # 取第一个别名
            alias = aliases[0]
            return f"{self.key}（{alias}）"
            
        # 如果没有别名，直接返回名称
        return self.key