
from evennia import DefaultObject
from typeclasses.templates.loader import TemplateLoader

class Item(DefaultObject):
    """
    自定义物品类，支持基于YAML模板的属性系统
    """

    def at_object_creation(self):
        """
        对象创建时调用，从模板加载默认属性
        """
        super().at_object_creation()

        # 获取物品类型
        item_type = getattr(self, 'itemType', 'base')

        # 加载物品模板
        template = TemplateLoader.load_template('items', item_type)
        if not template:
            # 如果模板加载失败，设置一些基本属性
            self.db.name = "未知物品"
            self.db.desc = "这是一个神秘的物品。"
            return

        # 将模板属性设置到物品db中
        for key, value in template.items():
            self.db[key] = value

        # 设置物品的key和显示名称
        self.key = self.db.name
        self.aliases.add(self.db.name.lower())
