from evennia.utils import create
from typeclasses.objects import StackableObject

# 模拟物品配置表 (未来可读 YAML)
ITEM_DATA = {
    # --- 资产类 (L1) ---
    "gold": {"type": "asset", "name": "金币"},
    "spirit_stone": {"type": "asset", "name": "下品灵石"},
    
    # --- 堆叠类 (L2) ---
    "pill_heal": {
        "type": "item", 
        "name": "回春丹", 
        "class": StackableObject,
        "desc": "一颗绿色的丹药，能恢复气血。"
    },
    "iron_ore": {
        "type": "item", 
        "name": "玄铁矿", 
        "class": StackableObject,
        "desc": "黑色的矿石，沉甸甸的。"
    }
}

def award_item(character, item_key, amount=1):
    """
    [核心开关] 
    根据配置表，自动决定是增加 Attr 数字，还是生成 Object。
    """
    data = ITEM_DATA.get(item_key)
    if not data:
        character.msg(f"错误：物品 {item_key} 不存在。")
        return

    # 分流逻辑
    if data["type"] == "asset":
        # 走 Attr 表 (L1)
        character.asset_handler.add(data["name"], amount)
        character.msg(f"你获得了 {amount} 个{data['name']}。")
        
    elif data["type"] == "item":
        # 走实体生成 (L2)
        # 1. 检查背包里有没有能堆叠的
        inventory = character.contents
        for obj in inventory:
            if isinstance(obj, StackableObject) and obj.key == data["name"]:
                obj.count += amount # 直接加数字
                character.msg(f"你捡起了 {data['name']} (x{amount}) [合并]。")
                return
        
        # 2. 没有则创建新对象
        new_obj = create.create_object(
            typeclass=data["class"],
            key=data["name"],
            location=character,
        )
        new_obj.db.desc = data["desc"]
        new_obj.count = amount # 设置初始数量
        character.msg(f"你捡起了 {data['name']} (x{amount})。")