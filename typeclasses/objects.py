"""
typeclasses/objects.py
物品与对象核心类 - 兼容修复版
"""
from evennia import DefaultObject
from evennia.utils import create

class Object(DefaultObject):
    """
    基础物品类。
    所有游戏内物品的基类。
    """
    def at_object_creation(self):
        super().at_object_creation()
        # 默认描述
        if not self.db.desc:
            self.db.desc = "一个普通的物品。"

class StackableObject(Object):
    """
    [核心] 可堆叠物品 (丹药、材料、消耗品)。
    特性: 自动合并、拆分、计数。
    """
    def at_object_creation(self):
        super().at_object_creation()
        self.db.stack_count = 1
        self.db.max_stack = 999
        self.db.stack_id = None 
        self.db.type_tag = "consumable" # 默认标签

    @property
    def count(self):
        return self.db.stack_count or 1

    @count.setter
    def count(self, value):
        val = max(0, int(value))
        self.db.stack_count = val
        # [安全机制] 归零自动销毁
        if val <= 0:
            self.delete()

    def get_display_name(self, looker, **kwargs):
        """显示时带上数量 (x99)"""
        name = super().get_display_name(looker, **kwargs)
        if self.count > 1:
            return f"{name} (x{self.count})"
        return name

    def can_stack_with(self, other):
        """判断是否是同一种东西"""
        if not isinstance(other, StackableObject): return False
        if self == other: return False
        if self.typeclass_path != other.typeclass_path: return False
        if self.key != other.key: return False
        if self.db.stack_id != other.db.stack_id: return False
        return True

    def merge_from(self, other):
        """合并逻辑"""
        if not self.can_stack_with(other): return False
        limit = self.db.max_stack or 999
        space = limit - self.count
        if space <= 0: return False

        transfer = min(space, other.count)
        if transfer > 0:
            self.count += transfer
            other.count -= transfer 
            return True
        return False

    def split(self, amount, location=None):
        """拆分逻辑"""
        amount = int(amount)
        if amount <= 0 or amount >= self.count:
            return None
        
        new_obj = create.create_object(
            typeclass=self.typeclass_path,
            key=self.key,
            location=location if location else self.location
        )
        new_obj.count = amount
        new_obj.db.desc = self.db.desc
        new_obj.db.stack_id = self.db.stack_id
        new_obj.db.effects = self.db.effects 
        new_obj.db.type_tag = self.db.type_tag
        
        self.count -= amount
        return new_obj

    def consume(self, amount=1):
        """消耗逻辑"""
        if self.count < amount: return False
        self.count -= amount
        return True

# =========================================================
# 兼容修复区域
# =========================================================

class Equipment(Object):
    """
    [兼容修复] 旧版本装备类。
    保留此类是为了防止数据库中已有的旧装备报错。
    """
    def at_object_creation(self):
        super().at_object_creation()
        self.db.type_tag = "equipment"

class Weapon(Equipment):
    """武器类"""
    def at_object_creation(self):
        super().at_object_creation()
        self.db.type_tag = "weapon"
        # 默认属性，防止报错
        if not self.db.stats:
            self.db.stats = {"strength": 10}

class Armor(Equipment):
    """防具类"""
    def at_object_creation(self):
        super().at_object_creation()
        self.db.type_tag = "armor"
        if not self.db.stats:
            self.db.stats = {"constitution": 10}
# =========================================================
# 新增：唯一物品类 (用于解决导入错误)
# =========================================================

class UniqueItem(Object):
    """
    唯一物品类 - 每个都是独立对象，不可堆叠
    用于装备、任务物品等
    """
    def at_object_creation(self):
        super().at_object_creation()
        # 基础属性
        self.db.item_key = ""
        self.db.template = {}
        self.db.enhance_level = 0
        self.db.durability = 100
        self.db.bound_to = None
        self.db.equipped = False  # 是否已装备
        
        # 默认描述
        if not self.db.desc:
            self.db.desc = "一件特殊的物品。"
    
    def get_display_name(self, looker, **kwargs):
        """获取显示名称（可重写以添加强化等级等）"""
        name = super().get_display_name(looker, **kwargs)
        if self.db.enhance_level and self.db.enhance_level > 0:
            return f"+{self.db.enhance_level} {name}"
        return name