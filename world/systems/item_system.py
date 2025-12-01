# world/systems/item_system.py
"""物品系统 - 预留词条和合成接口"""
from world.loaders.game_data import GAME_DATA, CONFIG

class ItemSystem:
    """物品系统（纯逻辑）"""
    
    def get_item_template(self, item_id):
        """获取物品模板"""
        return GAME_DATA['items'].get(item_id)
    
    def create_item_instance(self, item_id, with_affixes=False):
        """
        创建物品实例
        
        Args:
            item_id: 物品ID
            with_affixes: 是否生成随机词条（装备系统用）
        
        Returns:
            dict: 物品实例数据（可以存到角色的ndb.inventory）
        """
        template = self.get_item_template(item_id)
        if not template:
            return None
        
        instance = {
            'id': item_id,
            'name': template['name'],
            'type': template['type'],
            'stats': template.get('base_stats', {}).copy(),
            'affixes': [],  # 词条列表（以后扩展）
            'durability': template.get('base_stats', {}).get('durability', None)
        }
        
        # 预留：生成随机词条
        if with_affixes and template.get('affix_slots', 0) > 0:
            instance['affixes'] = self._generate_affixes(template)
        
        return instance
    
    def _generate_affixes(self, template):
        """
        生成随机词条（现在返回空列表，以后实现）
        
        预留接口：
        1. 根据 template['affix_slots'] 决定词条数量
        2. 从 GAME_DATA['affixes'] 随机抽取
        3. 应用词条到物品属性
        """
        # TODO: 以后实现词条系统时，在这里写逻辑
        return []
    
    def apply_affixes_to_stats(self, item_instance):
        """
        将词条效果应用到物品属性
        
        预留接口：遍历 item_instance['affixes']，累加属性
        """
        # TODO: 以后实现
        pass
    
    def can_craft(self, character, recipe_id):
        """
        检查是否可以合成
        
        预留接口：合成系统用
        """
        recipe = GAME_DATA['recipes'].get(recipe_id)
        if not recipe:
            return False, "配方不存在"
        
        # TODO: 检查材料、技能等级
        return True, "可以合成"
    
    def craft_item(self, character, recipe_id):
        """
        合成物品
        
        预留接口：合成系统用
        """
        # TODO: 以后实现合成系统
        pass
    
    def get_item_display_name(self, item_instance):
        """
        获取物品显示名称（包含词条）
        
        例如："锋利的玄铁重剑之吸血"
        """
        name = item_instance['name']
        
        # 预留：词条名称拼接
        affixes = item_instance.get('affixes', [])
        if affixes:
            prefix = [a['desc'] for a in affixes if a['type'] == 'prefix']
            suffix = [a['desc'] for a in affixes if a['type'] == 'suffix']
            
            if prefix:
                name = ''.join(prefix) + name
            if suffix:
                name = name + ''.join(suffix)
        
        return name