"""
world/systems/item_system.py
物品系统 - 重构版

核心功能：
1. give_item: 统一发奖接口（向下兼容）
2. ItemSystem: 物品查询与合成逻辑
"""
from world.loaders.game_data import GAME_DATA
from evennia.utils import logger


# =============================================================
# 1. 统一发奖接口（向下兼容旧代码）
# =============================================================

def give_item(character, item_key, amount=1):
    """
    [核心接口] 发放物品
    
    自动使用 InventoryHandler 管理物品
    向下兼容旧代码的调用方式
    
    Args:
        character: 接收物品的角色
        item_key: 物品ID（对应items.yaml的key）
        amount: 数量
    
    Returns:
        bool: 是否成功
    """
    if amount <= 0:
        return False
    
    # 检查角色是否有背包处理器
    if not hasattr(character, 'inventory'):
        from typeclasses.inventory_handler import InventoryHandler
        character.inventory = InventoryHandler(character)
    
    # 获取物品模板
    template = GAME_DATA.get('items', {}).get(item_key)
    if not template:
        character.msg(f"|r[系统] 物品ID '{item_key}' 不存在，请检查配置。|n")
        logger.log_warn(f"[物品] 未找到物品: {item_key}")
        return False
    
    # 使用InventoryHandler添加物品
    success = character.inventory.add(item_key, amount)
    
    if success:
        name = template.get('name', item_key)
        category = template.get('category', '物品')
        
        # 根据分类显示不同的提示
        if category == 'currency':
            character.msg(f"|y获得 {name} x{amount}|n")
        elif category == 'consumable':
            character.msg(f"|g获得 {name} x{amount}|n")
        elif category == 'equipment':
            character.msg(f"|c获得装备: {name}|n")
        else:
            character.msg(f"|g获得 {name} x{amount}|n")
    
    return success


# =============================================================
# 2. 物品系统逻辑类
# =============================================================

class ItemSystem:
    """
    物品系统（纯逻辑）
    
    负责：
    - 物品模板查询
    - 词条生成（预留）
    - 合成系统（预留）
    """
    
    def get_item_template(self, item_key):
        """
        获取物品模板
        
        Args:
            item_key: 物品ID
        
        Returns:
            dict: 物品模板数据，未找到返回None
        """
        return GAME_DATA.get('items', {}).get(item_key)
    
    def get_items_by_category(self, category):
        """
        按分类获取物品列表
        
        Args:
            category: 分类名称（'currency', 'consumable', 'equipment'等）
        
        Returns:
            dict: {item_key: template}
        """
        all_items = GAME_DATA.get('items', {})
        return {
            key: template 
            for key, template in all_items.items() 
            if template.get('category') == category
        }
    
    def search_items(self, keyword):
        """
        搜索物品（按名称模糊匹配）
        
        Args:
            keyword: 搜索关键词
        
        Returns:
            dict: {item_key: template}
        """
        all_items = GAME_DATA.get('items', {})
        keyword_lower = keyword.lower()
        
        return {
            key: template 
            for key, template in all_items.items() 
            if keyword_lower in template.get('name', '').lower() or keyword_lower in key.lower()
        }
    
    def can_use_item(self, character, item_key):
        """
        检查角色是否可以使用物品
        
        Args:
            character: 角色对象
            item_key: 物品ID
        
        Returns:
            tuple: (bool, str) - (是否可以使用, 原因)
        """
        template = self.get_item_template(item_key)
        if not template:
            return False, "物品不存在"
        
        # 检查是否拥有
        if not character.inventory.has(item_key, 1):
            return False, "物品不足"
        
        # 检查使用条件（预留接口）
        required_level = template.get('required_level', 0)
        if hasattr(character.db, 'level') and character.db.level < required_level:
            return False, f"需要等级 {required_level}"
        
        return True, ""
    
    def use_item(self, character, item_key, amount=1):
        """
        使用物品
        
        Args:
            character: 角色对象
            item_key: 物品ID
            amount: 使用数量
        
        Returns:
            bool: 是否成功
        """
        # 检查是否可以使用
        can_use, reason = self.can_use_item(character, item_key)
        if not can_use:
            character.msg(f"|r无法使用: {reason}|n")
            return False
        
        # 获取物品效果
        template = self.get_item_template(item_key)
        effects = template.get('effects', {})
        
        # 执行效果
        success = self._apply_effects(character, effects)
        
        if success:
            # 扣除物品
            character.inventory.remove(item_key, amount)
            character.msg(f"|g使用了 {template.get('name', item_key)}|n")
            return True
        
        return False
    
    def _apply_effects(self, character, effects):
        """
        应用物品效果
        
        Args:
            character: 角色对象
            effects: 效果字典
        
        Returns:
            bool: 是否成功
        """
        if not effects:
            return False
        
        action = effects.get('action')
        value = effects.get('value', 0)
        
        # 根据action类型执行不同效果
        if action == 'heal':
            # 恢复生命
            if hasattr(character.db, 'hp'):
                max_hp = getattr(character.db, 'max_hp', 100)
                character.db.hp = min(max_hp, character.db.hp + value)
                character.msg(f"|g恢复了 {value} 点生命值|n")
                return True
        
        elif action == 'restore_qi':
            # 恢复真气
            if hasattr(character.db, 'qi'):
                max_qi = getattr(character.db, 'max_qi', 100)
                character.db.qi = min(max_qi, character.db.qi + value)
                character.msg(f"|g恢复了 {value} 点真气|n")
                return True
        
        elif action == 'buff':
            # 添加BUFF（预留接口）
            character.msg(f"|y获得了 {effects.get('buff_name', '未知')} 效果|n")
            return True
        
        return False
    
    # ========== 合成系统（预留接口） ==========
    
    def get_recipe(self, recipe_id):
        """
        获取合成配方
        
        Args:
            recipe_id: 配方ID
        
        Returns:
            dict: 配方数据
        """
        return GAME_DATA.get('recipes', {}).get(recipe_id)
    
    def can_craft(self, character, recipe_id):
        """
        检查是否可以合成
        
        Args:
            character: 角色对象
            recipe_id: 配方ID
        
        Returns:
            tuple: (bool, str) - (是否可以, 原因)
        """
        recipe = self.get_recipe(recipe_id)
        if not recipe:
            return False, "配方不存在"
        
        # 检查材料
        materials = recipe.get('materials', {})
        for item_key, amount in materials.items():
            if not character.inventory.has(item_key, amount):
                template = self.get_item_template(item_key)
                name = template.get('name', item_key) if template else item_key
                return False, f"缺少材料: {name} x{amount}"
        
        return True, ""
    
    def craft_item(self, character, recipe_id):
        """
        合成物品
        
        Args:
            character: 角色对象
            recipe_id: 配方ID
        
        Returns:
            bool: 是否成功
        """
        # 检查是否可以合成
        can_craft, reason = self.can_craft(character, recipe_id)
        if not can_craft:
            character.msg(f"|r无法合成: {reason}|n")
            return False
        
        recipe = self.get_recipe(recipe_id)
        
        # 扣除材料
        materials = recipe.get('materials', {})
        for item_key, amount in materials.items():
            character.inventory.remove(item_key, amount)
        
        # 给予产物
        result = recipe.get('result', {})
        result_item = result.get('item_key')
        result_amount = result.get('amount', 1)
        
        give_item(character, result_item, result_amount)
        
        # 提示信息
        template = self.get_item_template(result_item)
        name = template.get('name', result_item) if template else result_item
        character.msg(f"|g成功合成 {name} x{result_amount}|n")
        
        return True