"""
world/systems/craft_system.py
合成系统 - 装备与材料合成

功能：
- 材料合成装备
- 装备+装备合成升级版
- 词条继承
- 合成成功率
"""
import random
from world.loaders.game_data import GAME_DATA
from world.systems.affix_system import AffixSystem
from evennia.utils import logger


class CraftSystem:
    """
    合成系统（纯逻辑）
    """
    
    def __init__(self):
        self.recipes = GAME_DATA.get('recipes', {})
        self.affix_system = AffixSystem()
    
    # ========== 合成检查 ==========
    
    def can_craft(self, character, recipe_id):
        """
        检查是否可以合成
        
        Args:
            character: 角色对象
            recipe_id: 配方ID
        
        Returns:
            tuple: (bool, str, dict) - (是否可以, 原因, 配方数据)
        """
        recipe = self.recipes.get(recipe_id)
        if not recipe:
            return False, "配方不存在", None
        
        # 检查材料
        materials = recipe.get('materials', {})
        for item_key, amount in materials.items():
            # 检查背包
            if not character.inventory.has(item_key, amount):
                from world.loaders.game_data import GAME_DATA
                template = GAME_DATA.get('items', {}).get(item_key, {})
                name = template.get('name', item_key)
                return False, f"缺少材料: {name} x{amount}", recipe
        
        # 检查等级需求
        required_level = recipe.get('required_level', 0)
        if hasattr(character.db, 'level') and character.db.level < required_level:
            return False, f"需要等级 {required_level}", recipe
        
        return True, "", recipe
    
    # ========== 材料合成装备 ==========
    
    def craft_equipment(self, character, recipe_id):
        """
        使用材料合成装备
        
        Args:
            character: 角色对象
            recipe_id: 配方ID
        
        Returns:
            tuple: (bool, str, obj) - (是否成功, 消息, 生成的装备)
        """
        # 检查是否可以合成
        can, reason, recipe = self.can_craft(character, recipe_id)
        if not can:
            return False, reason, None
        
        # 扣除材料
        materials = recipe.get('materials', {})
        for item_key, amount in materials.items():
            character.inventory.remove(item_key, amount)
        
        # 生成装备
        result = recipe.get('result', {})
        item_key = result.get('item_key')
        quality = result.get('quality', 'normal')  # normal/rare/epic
        
        # 使用装备生成器
        from world.systems.equipment_system import EquipmentSystem
        eq_system = EquipmentSystem()
        
        rarity_boost = self._get_rarity_boost(quality)
        equipment = eq_system.create_equipment(
            item_key,
            location=character,
            rarity_boost=rarity_boost
        )
        
        if not equipment:
            return False, "生成装备失败", None
        
        return True, f"成功合成 {equipment.get_display_name(character)}", equipment
    
    # ========== 装备合并 ==========
    
    def merge_equipment(self, character, recipe_id, source_items):
        """
        合并多个装备成更高级装备
        
        Args:
            character: 角色对象
            recipe_id: 配方ID
            source_items: 源装备列表（UniqueItem对象）
        
        Returns:
            tuple: (bool, str, obj) - (是否成功, 消息, 新装备)
        """
        recipe = self.recipes.get(recipe_id)
        if not recipe or recipe.get('type') != 'equipment_merge':
            return False, "配方类型错误", None
        
        # 检查源装备数量
        required_count = recipe.get('source_count', 2)
        if len(source_items) != required_count:
            return False, f"需要 {required_count} 个装备", None
        
        # 检查源装备是否符合要求
        required_item_key = recipe.get('source_item')
        for item in source_items:
            if item.db.item_key != required_item_key:
                return False, "装备类型不匹配", None
        
        # 扣除金币或其他材料
        materials = recipe.get('materials', {})
        for item_key, amount in materials.items():
            if not character.inventory.remove(item_key, amount):
                return False, f"材料不足: {item_key}", None
        
        # 词条继承策略
        inherit_strategy = recipe.get('inherit_affixes', 'best')
        inherited_affixes = self.affix_system.inherit_affixes(
            source_items,
            strategy=inherit_strategy
        )
        
        # 生成新装备
        result_item_key = recipe.get('result', {}).get('item_key')
        from world.systems.equipment_system import EquipmentSystem
        eq_system = EquipmentSystem()
        
        new_equipment = eq_system.create_equipment(
            result_item_key,
            location=character,
            rarity_boost=1  # 合成品略微提升品质
        )
        
        if not new_equipment:
            return False, "生成装备失败", None
        
        # 应用继承的词条（限制数量）
        max_affixes = new_equipment.db.template.get('affix_slots', 3)
        new_equipment.db.affixes = inherited_affixes[:max_affixes]
        
        # 删除源装备
        for item in source_items:
            item.delete()
        
        return True, f"成功合成 {new_equipment.get_display_name(character)}", new_equipment
    
    # ========== 装备升级 ==========
    
    def upgrade_equipment(self, equipment, materials):
        """
        使用材料升级装备
        
        Args:
            equipment: 装备对象
            materials: {item_key: amount}
        
        Returns:
            tuple: (bool, str) - (是否成功, 消息)
        """
        # 检查是否已满级
        current_level = equipment.db.enhance_level or 0
        max_level = equipment.db.template.get('enhance_max', 15)
        
        if current_level >= max_level:
            return False, "已达到最高强化等级"
        
        # TODO: 实现升级逻辑
        # 这里可以根据材料品质决定成功率
        
        success_rate = 0.8  # 基础成功率80%
        
        if random.random() < success_rate:
            equipment.db.enhance_level = current_level + 1
            return True, f"强化成功！当前等级 +{equipment.db.enhance_level}"
        else:
            # 失败可能降级
            if current_level >= 5:
                equipment.db.enhance_level = max(0, current_level - 1)
                return False, f"强化失败！装备降级至 +{equipment.db.enhance_level}"
            else:
                return False, "强化失败！装备未受损"
    
    # ========== 辅助方法 ==========
    
    def _get_rarity_boost(self, quality):
        """
        根据品质获取稀有度加成
        
        Args:
            quality: 'normal', 'random', 'rare', 'epic'
        
        Returns:
            int: 稀有度加成
        """
        if quality == 'random':
            return random.randint(0, 2)
        
        boosts = {
            'normal': 0,
            'rare': 1,
            'epic': 2,
            'legendary': 3
        }
        
        return boosts.get(quality, 0)
    
    # ========== 配方查询 ==========
    
    def get_recipe(self, recipe_id):
        """获取配方数据"""
        return self.recipes.get(recipe_id)
    
    def get_recipes_by_type(self, craft_type):
        """
        按类型获取配方
        
        Args:
            craft_type: 'equipment', 'equipment_merge', 'consumable'
        
        Returns:
            dict: {recipe_id: recipe}
        """
        return {
            rid: recipe for rid, recipe in self.recipes.items()
            if recipe.get('type') == craft_type
        }
    
    def search_recipes(self, keyword):
        """
        搜索配方
        
        Args:
            keyword: 关键词
        
        Returns:
            dict: {recipe_id: recipe}
        """
        keyword_lower = keyword.lower()
        
        return {
            rid: recipe for rid, recipe in self.recipes.items()
            if keyword_lower in recipe.get('name', '').lower()
        }


class EquipmentSystem:
    """
    装备生成系统
    """
    
    def __init__(self):
        self.affix_system = AffixSystem()
    
    def create_equipment(self, item_key, location=None, rarity_boost=0, affixes=None):
        """
        创建装备实例
        
        Args:
            item_key: 装备ID
            location: 生成位置
            rarity_boost: 稀有度加成
            affixes: 指定词条（None则随机生成）
        
        Returns:
            UniqueItem: 装备对象
        """
        from evennia.utils import create
        from world.loaders.game_data import GAME_DATA
        
        template = GAME_DATA.get('items', {}).get(item_key)
        if not template:
            logger.log_warn(f"[装备] 装备不存在: {item_key}")
            return None
        
        # 创建对象
        equipment = create.create_object(
            typeclass="typeclasses.objects.UniqueItem",
            key=template.get('name', item_key),
            location=location
        )
        
        # 存储模板数据
        equipment.db.item_key = item_key
        equipment.db.template = template
        
        # 初始化属性
        equipment.db.enhance_level = 0
        equipment.db.durability = template.get('base_stats', {}).get('durability', 100)
        equipment.db.bound_to = None
        
        # 生成词条
        if affixes is None:
            affixes = self.affix_system.generate_affixes(
                item_key,
                rarity_boost=rarity_boost
            )
        
        equipment.db.affixes = affixes
        
        logger.log_info(f"[装备] 生成: {equipment.key} (词条x{len(affixes)})")
        
        return equipment