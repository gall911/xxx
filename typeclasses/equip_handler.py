"""
typeclasses/equip_handler.py
装备处理器 - 修复版
解决 at_init 调用时尝试写数据库导致的崩溃问题
"""
from world.loaders.game_data import get_config, get_data
import yaml
import os

class EquipHandler:
    """
    挂载在 Character 上的装备管理器
    数据存储: self.owner.db.equipment = {'main_hand': obj, ...}
    """
    def __init__(self, owner):
        self.owner = owner
        self.slot_config = self._load_slots()

    def _load_slots(self):
        """读取 yaml 配置"""
        try:
            with open("data/equip_slots.yaml", 'r', encoding='utf-8') as f:
                return yaml.safe_load(f).get('slots', {})
        except:
            return {}

    @property
    def equipped_items(self):
        """
        获取当前已装备的 {slot: Object} 字典
        【核心修复】: 这里只做过滤，绝对不要执行 db 写入操作！
        """
        raw_eq = self.owner.db.equipment
        if not raw_eq:
            return {}
        
        valid_eq = {}
        
        # 遍历数据库里的记录
        for slot, item in raw_eq.items():
            # 检查 item 是否存在且有效 (item.pk 用于判断对象是否仍在数据库中)
            if item and hasattr(item, 'pk') and item.pk:
                valid_eq[slot] = item
        
        # 注意：不要在这里写回 self.owner.db.equipment = valid_eq
        # 即使发现有脏数据，at_init 阶段也不能写库。
        # 脏数据会在下次玩家执行 equip/unequip 时自然被覆盖或清理。
            
        return valid_eq

    def get_slot_info(self, slot_key):
        return self.slot_config.get(slot_key)

    def equip(self, obj):
        """
        穿戴物品
        """
        # 1. 检查类型
        obj_type = obj.db.type_tag 
        target_slot = None

        # 智能匹配插槽
        available_slots = []
        for slot, conf in self.slot_config.items():
            accepts = conf.get('accepts', [])
            if obj_type in accepts:
                available_slots.append(slot)
        
        if not available_slots:
            return False, "这件东西没法装备，或者没有对应的部位。"

        # 2. 找位置
        final_slot = available_slots[0]
        # 优先找空位
        current_eq = self.equipped_items # 读取当前有效装备
        
        for slot in available_slots:
            if slot not in current_eq:
                final_slot = slot
                break
        
        # 3. 顶替旧装备
        if final_slot in current_eq:
            self.unequip(final_slot)

        # 4. 执行穿戴 (这里写库是安全的，因为是命令触发)
        if not self.owner.db.equipment:
            self.owner.db.equipment = {}
            
        self.owner.db.equipment[final_slot] = obj
        
        # 移动到虚空 (避免在背包显示)
        obj.location = None 
        
        obj.db.is_equipped = True
        obj.db.equipped_slot = final_slot
        
        # 5. 触发钩子
        if hasattr(obj, "at_equip"):
            obj.at_equip(self.owner)

        # 6. 同步属性
        if hasattr(self.owner, "sync_stats_to_ndb"):
            self.owner.sync_stats_to_ndb()
        
        slot_name = self.slot_config.get(final_slot, {}).get('name', final_slot)
        return True, f"你装备了 {obj.key} 到 {slot_name}。"

    def unequip(self, slot):
        """
        卸下物品
        """
        current_eq = self.equipped_items
        if slot not in current_eq:
            return False, "那个位置没有装备。"
        
        obj = current_eq[slot]
        
        # 1. 移除记录
        # 直接操作 db 字典需要重新赋值才能触发 Evennia 保存
        eq_dict = self.owner.db.equipment
        if slot in eq_dict:
            del eq_dict[slot]
            self.owner.db.equipment = eq_dict 
        
        # 2. 还原状态
        obj.location = self.owner # 回到背包
        obj.db.is_equipped = False
        obj.db.equipped_slot = None
        
        # 3. 触发钩子
        if hasattr(obj, "at_unequip"):
            obj.at_unequip(self.owner)
            
        # 4. 同步
        if hasattr(self.owner, "sync_stats_to_ndb"):
            self.owner.sync_stats_to_ndb()
        
        return True, f"你卸下了 {obj.key}。"

    def get_total_stats(self):
        """
        汇总所有装备提供的属性
        """
        total = {}
        # 这里调用 self.equipped_items，它现在是安全的只读操作
        for slot, item in self.equipped_items.items():
            stats = item.db.stats or {}
            for key, val in stats.items():
                total[key] = total.get(key, 0) + val
        return total