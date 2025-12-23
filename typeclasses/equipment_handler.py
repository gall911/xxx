"""
typeclasses/equipment_handler.py
装备处理器 - 全新版本

特性：
- 与 InventoryHandler 集成
- 支持装备槽位管理
- 实时属性同步
- 装备耐久度管理
"""
from evennia.utils import logger
from world.loaders.game_data import GAME_DATA


class EquipmentHandler:
    """
    装备处理器（挂在角色的 character.equipment）
    
    装备数据存储：character.db.equipped = {slot: item_obj}
    """
    
    def __init__(self, character):
        self.character = character
        
        # 初始化装备槽位
        if not hasattr(character.db, 'equipped'):
            character.db.equipped = {}
        
        # 加载槽位配置
        self.slots = GAME_DATA.get('equip_slots', {})
    
    # ========== 装备管理 ==========
    
    def equip(self, item_obj):
        """
        穿戴装备
        
        Args:
            item_obj: UniqueItem对象
        
        Returns:
            tuple: (bool, str) - (是否成功, 消息)
        """
        from typeclasses.objects import UniqueItem
        
        # 检查是否是装备
        if not isinstance(item_obj, UniqueItem):
            return False, "这不是装备"
        
        # 检查是否在背包
        if item_obj.location != self.character:
            return False, "装备不在背包里"
        
        # 获取装备槽位
        slot = item_obj.db.template.get('slot')
        if not slot:
            return False, "这件装备没有定义槽位"
        
        # 检查槽位是否存在
        slot_config = self.slots.get(slot)
        if not slot_config:
            return False, f"未知的装备槽位: {slot}"
        
        # 检查等级需求
        required_level = item_obj.db.template.get('required_level', 0)
        if hasattr(self.character.db, 'level') and self.character.db.level < required_level:
            return False, f"需要等级 {required_level}"
        
        # 检查是否已有装备（需要先卸下）
        current_equipped = self.character.db.equipped
        if slot in current_equipped:
            old_item = current_equipped[slot]
            if old_item and hasattr(old_item, 'pk') and old_item.pk:
                self.unequip(slot)
        
        # 穿戴装备
        self.character.db.equipped[slot] = item_obj
        item_obj.db.equipped = True
        item_obj.db.equipped_slot = slot
        item_obj.location = None  # 从背包移除
        
        # 同步属性
        self._sync_stats()
        
        # 触发钩子
        if hasattr(item_obj, 'at_equip'):
            item_obj.at_equip(self.character)
        
        slot_name = slot_config.get('name', slot)
        return True, f"装备 {item_obj.get_display_name(self.character)} 到 {slot_name}"
    
    def unequip(self, slot):
        """
        卸下装备
        
        Args:
            slot: 装备槽位
        
        Returns:
            tuple: (bool, str) - (是否成功, 消息)
        """
        current_equipped = self.character.db.equipped
        
        if slot not in current_equipped:
            return False, "该槽位没有装备"
        
        item_obj = current_equipped[slot]
        
        # 检查对象是否有效
        if not item_obj or not hasattr(item_obj, 'pk') or not item_obj.pk:
            # 清理无效引用
            del current_equipped[slot]
            self.character.db.equipped = current_equipped
            return False, "装备已不存在"
        
        # 卸下装备
        del current_equipped[slot]
        self.character.db.equipped = current_equipped
        
        item_obj.db.equipped = False
        item_obj.db.equipped_slot = None
        item_obj.location = self.character  # 放回背包
        
        # 同步属性
        self._sync_stats()
        
        # 触发钩子
        if hasattr(item_obj, 'at_unequip'):
            item_obj.at_unequip(self.character)
        
        return True, f"卸下 {item_obj.get_display_name(self.character)}"
    
    def unequip_all(self):
        """
        卸下所有装备
        
        Returns:
            int: 卸下的装备数量
        """
        slots = list(self.character.db.equipped.keys())
        count = 0
        
        for slot in slots:
            success, _ = self.unequip(slot)
            if success:
                count += 1
        
        return count
    
    # ========== 查询功能 ==========
    
    def get_equipped(self, slot=None):
        """
        获取已装备的物品
        
        Args:
            slot: 槽位名称，None则返回所有
        
        Returns:
            dict或object: 装备字典或单个装备对象
        """
        current_equipped = self.character.db.equipped
        
        if slot:
            return current_equipped.get(slot)
        
        # 清理无效引用
        valid = {}
        for s, item in current_equipped.items():
            if item and hasattr(item, 'pk') and item.pk:
                valid[s] = item
        
        return valid
    
    def get_total_stats(self):
        """
        获取所有装备提供的属性加成
        
        Returns:
            dict: {属性名: 值}
        """
        total = {}
        
        for slot, item in self.get_equipped().items():
            stats = item.get_stats()
            for key, value in stats.items():
                if key == 'durability':
                    continue  # 耐久度不参与加成
                total[key] = total.get(key, 0) + value
        
        return total
    
    def list_equipped(self):
        """
        列出所有已装备的物品（用于显示）
        
        Returns:
            list: [{slot, slot_name, item, stats}, ...]
        """
        result = []
        
        equipped = self.get_equipped()
        
        # 按槽位顺序排序
        sorted_slots = sorted(
            self.slots.items(),
            key=lambda x: x[1].get('order', 99)
        )
        
        for slot, slot_config in sorted_slots:
            slot_name = slot_config.get('name', slot)
            item = equipped.get(slot)
            
            if item:
                result.append({
                    'slot': slot,
                    'slot_name': slot_name,
                    'item': item,
                    'stats': item.get_stats()
                })
            else:
                result.append({
                    'slot': slot,
                    'slot_name': slot_name,
                    'item': None,
                    'stats': {}
                })
        
        return result
    
    # ========== 耐久度管理 ==========
    
    def damage_equipment(self, slot, damage=1):
        """
        损耗装备耐久度
        
        Args:
            slot: 装备槽位
            damage: 损耗值
        
        Returns:
            bool: 是否成功
        """
        item = self.get_equipped(slot)
        if not item:
            return False
        
        old_dur = item.db.durability
        new_dur = max(0, old_dur - damage)
        item.db.durability = new_dur
        
        # 耐久度归零时自动卸下
        if new_dur <= 0:
            self.character.msg(f"|r{item.key} 已损坏！|n")
            self.unequip(slot)
        
        return True
    
    def damage_all_equipment(self, damage=1):
        """
        损耗所有装备耐久度
        
        Args:
            damage: 损耗值
        """
        for slot in self.get_equipped().keys():
            self.damage_equipment(slot, damage)
    
    # ========== 属性同步 ==========
    
    def _sync_stats(self):
        """
        同步装备属性到角色
        """
        # 如果角色有属性同步方法，调用它
        if hasattr(self.character, 'sync_stats_to_ndb'):
            self.character.sync_stats_to_ndb()
        
        # 如果有战斗系统，更新战斗属性
        if hasattr(self.character, 'update_combat_stats'):
            self.character.update_combat_stats()
    
    # ========== 便捷方法 ==========
    
    def has_equipped(self, slot):
        """
        检查某个槽位是否有装备
        
        Args:
            slot: 槽位名称
        
        Returns:
            bool: 是否有装备
        """
        return slot in self.get_equipped()
    
    def get_equipment_count(self):
        """
        获取已装备的物品数量
        
        Returns:
            int: 装备数量
        """
        return len(self.get_equipped())
    
    def get_empty_slots(self):
        """
        获取空闲的装备槽位
        
        Returns:
            list: 空槽位列表
        """
        equipped = self.get_equipped()
        return [slot for slot in self.slots.keys() if slot not in equipped]