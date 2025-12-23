"""
typeclasses/inventory_handler.py
背包处理器 - 最终修正版
修复了缩进错误，补全了容量检查方法
"""
from evennia.utils import logger

class InventoryHandler:
    """
    背包处理器（挂在角色的 character.inventory）
    """
    
    def __init__(self, character):
        self.character = character
        
        # 1. 确保 ndb 存在
        if not hasattr(character, 'ndb'):
            from evennia.utils.utils import lazy_property
            character.ndb = lazy_property()
        
        # 2. 确保 items 字典存在
        if not hasattr(character.ndb, 'items') or character.ndb.items is None:
            character.ndb.items = {}
        
        # 3. 加载数据
        if not hasattr(character.ndb, '_items_loaded') or not character.ndb._items_loaded:
            self._load_from_persistent()
            character.ndb._items_loaded = True

    # ========== 容量管理 (修复报错的核心) ==========

    def get_capacity(self):
        """获取角色当前的最大背包容量"""
        from world.loaders.game_data import GAME_DATA, get_config
        
        # 1. 获取境界加成（优先使用境界特定配置）
        realm_name = self.character.db.realm
        if realm_name:
            # 修复：GAME_DATA['realms']已经包含realms对象，需要再次获取realms键
            realms_data = GAME_DATA.get('realms', {})
            if isinstance(realms_data, dict) and 'realms' in realms_data:
                realms_data = realms_data['realms']
                
            realm_data = realms_data.get(realm_name, {})
            # 优先使用境界中的default_inventory_size配置，如果没有则使用inventory_size
            realm_size = realm_data.get('default_inventory_size')
            if realm_size is None:
                realm_size = realm_data.get('inventory_size')
            
            if realm_size is not None:
                return realm_size
        
        # 2. 如果没有境界特定配置，使用全局配置
        return get_config('game.default_inventory_size', 20)

    def get_usage(self):
        """
        获取已用格子数
        规则：
        - 堆叠物品：每种占用 1 格
        - 唯一物品：每个占用 1 格 (已装备的不算)
        """
        # 堆叠物品种类数
        stackable_count = len(self.character.ndb.items)
        
        # 唯一物品数量 (只计算背包里的，不计算已装备的)
        unique_objs = self.get_unique_items()
        unique_count = len(unique_objs)
        
        return stackable_count + unique_count
    
    # ========== 持久化管理 ==========
    
    def _load_from_persistent(self):
        """从 attr 加载到 ndb"""
        saved = self.character.attributes.get('inventory_data', default={})
        if saved:
            self.character.ndb.items = dict(saved)
        else:
            self.character.ndb.items = {}
    
    def _save_to_persistent(self):
        """从 ndb 保存到 attr"""
        from world.loaders.game_data import GAME_DATA
        to_save = {}
        for item_key, count in self.character.ndb.items.items():
            template = GAME_DATA.get('items', {}).get(item_key)
            if template and template.get('storage', 'attr') == 'attr':
                to_save[item_key] = count
        self.character.attributes.add('inventory_data', to_save)
    
    def _schedule_save(self):
        """延迟保存"""
        from evennia.utils import delay
        if hasattr(self.character.ndb, '_save_task'):
            try: self.character.ndb._save_task.cancel()
            except: pass
        self.character.ndb._save_task = delay(1, self._save_to_persistent)
    
    def force_save(self):
        """强制保存"""
        if hasattr(self.character.ndb, '_save_task'):
            try: self.character.ndb._save_task.cancel()
            except: pass
        self._save_to_persistent()
    
    # ========== 物品操作 ==========
    
    def add(self, item_key, amount=1):
        """添加物品 (带容量检查)"""
        from world.loaders.game_data import GAME_DATA
        
        if amount <= 0: return False
        
        template = GAME_DATA.get('items', {}).get(item_key)
        if not template:
            logger.log_warn(f"[背包] 未知物品: {item_key}")
            return False
        
        storage = template.get('storage', 'attr')
        stackable = template.get('stackable', True)
        
        # 🔥 容量检查
        current_usage = self.get_usage()
        max_capacity = self.get_capacity()
        
        if storage == 'db':
            # 唯一物品：每件占一格
            if current_usage + amount > max_capacity:
                self.character.msg("|r背包已满！无法携带更多装备。|n")
                return False
        elif stackable:
            # 堆叠物品：只有新种类才占格
            if item_key not in self.character.ndb.items:
                if current_usage + 1 > max_capacity:
                    self.character.msg("|r背包已满！无法容纳新物品。|n")
                    return False
        
        # 执行添加
        if storage == 'db':
            return self._create_unique_items(item_key, template, amount)
        elif stackable:
            current = self.character.ndb.items.get(item_key, 0)
            self.character.ndb.items[item_key] = current + amount
            if storage == 'attr':
                self._schedule_save()
            return True
        else:
            return False
    
    def remove(self, item_key, amount=1):
        """移除物品"""
        if amount <= 0: return False
        
        current = self.character.ndb.items.get(item_key, 0)
        if current < amount:
            return False
        
        new_count = current - amount
        if new_count <= 0:
            del self.character.ndb.items[item_key]
        else:
            self.character.ndb.items[item_key] = new_count
            
        # 触发保存
        from world.loaders.game_data import GAME_DATA
        template = GAME_DATA.get('items', {}).get(item_key, {})
        if template.get('storage', 'attr') == 'attr':
            self._schedule_save()
        return True
    
    def get(self, item_key):
        return self.character.ndb.items.get(item_key, 0)
    
    def has(self, item_key, amount=1):
        return self.get(item_key) >= amount
    
    # ========== 唯一物品管理 (别名支持) ==========
    
    def _create_unique_items(self, item_key, template, amount):
        """创建唯一物品"""
        from evennia.utils import create
        created = []
        
        # 1. 准备别名
        alias_set = {item_key} 
        yaml_aliases = template.get('aliases', [])
        
        if yaml_aliases:
            if isinstance(yaml_aliases, str):
                for a in yaml_aliases.split(','):
                    if a.strip(): alias_set.add(a.strip())
            elif isinstance(yaml_aliases, list):
                for a in yaml_aliases:
                    if str(a).strip(): alias_set.add(str(a).strip())
        
        final_aliases = list(alias_set)

        for _ in range(amount):
            # 2. 创建对象
            obj = create.create_object(
                typeclass="typeclasses.objects.UniqueItem",
                key=template.get('name', item_key),
                location=self.character,
                aliases=final_aliases
            )
            
            # 3. 写入数据
            if template.get('desc'):
                obj.db.desc = template['desc']
            obj.db.item_key = item_key
            obj.db.template = template
            obj.db.enhance_level = 0
            obj.db.durability = template.get('base_stats', {}).get('durability', 100)
            obj.db.bound_to = None
            
            created.append(obj)
        
        return True
    
    def get_unique_items(self):
        """获取背包里的唯一物品（排除已装备的）"""
        from typeclasses.objects import UniqueItem
        # 🔥 关键修改：只返回没装备的
        return [
            obj for obj in self.character.contents 
            if isinstance(obj, UniqueItem) and not obj.db.equipped
        ]
    
    # ========== 查询与显示 ==========
    
    def list_items(self, category=None):
        """列出物品"""
        from world.loaders.game_data import GAME_DATA
        result = []
        
        # 堆叠物品
        for item_key, count in self.character.ndb.items.items():
            template = GAME_DATA.get('items', {}).get(item_key, {})
            item_cat = template.get('category', 'misc')
            if category and item_cat != category: continue
            
            result.append({
                'key': item_key,
                'name': template.get('name', item_key),
                'count': count,
                'category': item_cat,
                'storage': template.get('storage', 'attr')
            })
        
        # 唯一物品 (调用 get_unique_items，所以这里也不包含已装备的)
        target_objs = self.get_unique_items()
        
        for obj in target_objs:
            template = obj.db.template or {}
            item_cat = template.get('category', 'equipment')
            
            if category and item_cat != category: continue
            
            result.append({
                'key': obj.db.item_key,
                'name': obj.key,
                'count': 1,
                'category': item_cat,
                'storage': 'db',
                'object': obj
            })
        
        return result

    def transfer_to(self, target, item_key, amount=1):
        """转移物品"""
        if not hasattr(target, 'inventory'): return False
        
        # 堆叠物品转移
        if self.remove(item_key, amount):
            if not target.inventory.add(item_key, amount):
                self.add(item_key, amount) # 回滚
                return False
            return True
        return False