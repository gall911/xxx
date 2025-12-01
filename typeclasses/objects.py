"""
物品类型类
"""
from evennia import DefaultObject

# typeclasses/objects.py
from evennia.utils import utils

class ObjectParent:
    """
    所有对象的通用混入类
    """
    def get_display_name(self, looker, **kwargs):
        """
        决定对象在 look 时显示的名字
        我们将其改为： 彩色中文名(英文Key)
        """
        # 如果有 color_name (我们在 yaml 里配的那个 |513西域魅魔|n)，就用它
        if self.db.color_name:
            display = f"{self.db.color_name}"
        else:
            display = self.key
            
        # 加上英文 key 以便交互
        # 效果：|513西域魅魔|n(mirage_witch)
        # 这样玩家就知道输入 'look mirage_witch' 肯定能行
        return f"{display}({self.key})"

    pass

class Object(ObjectParent, DefaultObject):
    """
    基础物品类
    这是所有游戏内实体物品的基类
    """
    
    def at_object_creation(self):
        """物品创建时初始化"""
        super().at_object_creation()
        
        # 物品类型
        self.db.item_type = "misc"
        
        # 是否可堆叠
        self.db.stackable = False
        self.db.stack_max = 1
        
        # 价格
        self.db.price = 0

class Consumable(Object):
    """
    消耗品（丹药等）
    """
    
    def at_object_creation(self):
        """初始化"""
        super().at_object_creation()
        
        self.db.item_type = "consumable"
        self.db.stackable = True
        self.db.stack_max = 99
        
        # 效果配置
        self.db.effects = {}
    
    def use(self, user):
        """
        使用消耗品
        
        Args:
            user: 使用者
        
        Returns:
            bool: 是否使用成功
        """
        # TODO: 应用效果
        return True

class Equipment(Object):
    """
    装备（武器、防具等）
    """
    
    def at_object_creation(self):
        """初始化"""
        super().at_object_creation()
        
        self.db.item_type = "equipment"
        self.db.stackable = False
        
        # 装备槽位
        self.db.slot = "weapon"  # weapon, armor, accessory等
        
        # 基础属性
        self.db.base_stats = {}
        
        # 词条
        self.db.affixes = []