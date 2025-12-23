"""
world/systems/affix_system.py
词条系统 - 装备随机属性生成

功能：
- 随机生成词条
- 词条品质系统
- 词条重铸
- 词条继承（合成时）
"""
import random
from world.loaders.game_data import GAME_DATA
from evennia.utils import logger


class AffixSystem:
    """
    词条系统（纯逻辑）
    """
    
    def __init__(self):
        self.affixes = GAME_DATA.get('affixes', {})
    
    # ========== 词条生成 ==========
    
    def generate_affixes(self, equipment_key, count=None, rarity_boost=0):
        """
        为装备生成随机词条
        
        Args:
            equipment_key: 装备ID
            count: 词条数量（None则根据装备配置）
            rarity_boost: 稀有度加成（影响词条品质）
        
        Returns:
            list: [{affix_data}, ...]
        """
        from world.loaders.game_data import GAME_DATA
        
        template = GAME_DATA.get('items', {}).get(equipment_key)
        if not template:
            logger.log_warn(f"[词条] 装备不存在: {equipment_key}")
            return []
        
        # 确定词条数量
        if count is None:
            count = template.get('affix_slots', 0)
        
        if count <= 0:
            return []
        
        # 生成词条
        generated = []
        prefix_count = 0
        suffix_count = 0
        
        for _ in range(count):
            # 随机选择前缀或后缀
            affix_type = self._choose_affix_type(prefix_count, suffix_count)
            
            # 选择词条
            affix = self._select_random_affix(affix_type, rarity_boost)
            
            if affix:
                generated.append(affix)
                if affix['type'] == 'prefix':
                    prefix_count += 1
                else:
                    suffix_count += 1
        
        return generated
    
    def _choose_affix_type(self, prefix_count, suffix_count):
        """
        选择词条类型（前缀/后缀）
        
        策略：保持平衡，但允许随机
        """
        if prefix_count == 0 and suffix_count == 0:
            return random.choice(['prefix', 'suffix'])
        
        if prefix_count > suffix_count:
            # 前缀多了，偏向后缀
            return random.choices(['prefix', 'suffix'], weights=[0.3, 0.7])[0]
        elif suffix_count > prefix_count:
            # 后缀多了，偏向前缀
            return random.choices(['prefix', 'suffix'], weights=[0.7, 0.3])[0]
        else:
            # 平衡，随机
            return random.choice(['prefix', 'suffix'])
    
    def _select_random_affix(self, affix_type, rarity_boost=0):
        """
        随机选择一个词条
        
        Args:
            affix_type: 'prefix' 或 'suffix'
            rarity_boost: 稀有度加成
        
        Returns:
            dict: 词条数据
        """
        # 筛选指定类型的词条
        candidates = [
            affix for affix in self.affixes.values()
            if affix.get('type') == affix_type
        ]
        
        if not candidates:
            return None
        
        # 根据tier（品质）加权
        weights = []
        for affix in candidates:
            tier = affix.get('tier', 1)
            # 高tier的词条更稀有，权重更低
            # 但rarity_boost可以提高高tier的概率
            base_weight = 100 / (tier ** 1.5)
            boosted_weight = base_weight * (1 + rarity_boost * 0.2)
            weights.append(boosted_weight)
        
        # 加权随机选择
        selected = random.choices(candidates, weights=weights)[0]
        
        # 深拷贝词条数据
        return self._copy_affix(selected)
    
    def _copy_affix(self, affix):
        """深拷贝词条数据"""
        import copy
        return copy.deepcopy(affix)
    
    # ========== 词条应用 ==========
    
    def apply_affixes_to_stats(self, base_stats, affixes):
        """
        将词条效果应用到基础属性
        
        Args:
            base_stats: 基础属性字典
            affixes: 词条列表
        
        Returns:
            dict: 应用词条后的属性
        """
        result = base_stats.copy()
        
        for affix in affixes:
            # 应用属性加成
            stats = affix.get('stats', {})
            for key, value in stats.items():
                result[key] = result.get(key, 0) + value
        
        return result
    
    def get_affix_effects(self, affixes):
        """
        获取词条的特殊效果
        
        Args:
            affixes: 词条列表
        
        Returns:
            list: 效果列表
        """
        effects = []
        
        for affix in affixes:
            affix_effects = affix.get('effects', [])
            effects.extend(affix_effects)
        
        return effects
    
    # ========== 词条重铸 ==========
    
    def reroll_affix(self, equipment_obj, index, rarity_boost=0):
        """
        重铸单个词条
        
        Args:
            equipment_obj: 装备对象
            index: 词条索引
            rarity_boost: 稀有度加成
        
        Returns:
            bool: 是否成功
        """
        affixes = equipment_obj.db.affixes or []
        
        if index < 0 or index >= len(affixes):
            return False
        
        old_affix = affixes[index]
        affix_type = old_affix.get('type', 'prefix')
        
        # 生成新词条（同类型）
        new_affix = self._select_random_affix(affix_type, rarity_boost)
        
        if new_affix:
            affixes[index] = new_affix
            equipment_obj.db.affixes = affixes
            return True
        
        return False
    
    def reroll_all_affixes(self, equipment_obj, rarity_boost=0):
        """
        重铸所有词条
        
        Args:
            equipment_obj: 装备对象
            rarity_boost: 稀有度加成
        
        Returns:
            int: 重铸成功的数量
        """
        affixes = equipment_obj.db.affixes or []
        count = len(affixes)
        
        new_affixes = self.generate_affixes(
            equipment_obj.db.item_key,
            count=count,
            rarity_boost=rarity_boost
        )
        
        equipment_obj.db.affixes = new_affixes
        
        return len(new_affixes)
    
    # ========== 词条继承 ==========
    
    def inherit_affixes(self, source_items, strategy='best'):
        """
        从多个装备中继承词条
        
        Args:
            source_items: 源装备列表
            strategy: 继承策略
                - 'best': 选择最好的词条
                - 'random': 随机选择
                - 'merge': 合并所有（可能超出槽位）
        
        Returns:
            list: 继承的词条列表
        """
        all_affixes = []
        
        # 收集所有词条
        for item in source_items:
            affixes = item.db.affixes or []
            all_affixes.extend(affixes)
        
        if not all_affixes:
            return []
        
        if strategy == 'best':
            # 按tier排序，选择最好的
            sorted_affixes = sorted(
                all_affixes,
                key=lambda x: x.get('tier', 1),
                reverse=True
            )
            return sorted_affixes
        
        elif strategy == 'random':
            # 随机打乱
            random.shuffle(all_affixes)
            return all_affixes
        
        elif strategy == 'merge':
            # 全部合并
            return all_affixes
        
        return all_affixes
    
    # ========== 显示功能 ==========
    
    def get_affix_display_name(self, affixes):
        """
        获取带词条的装备名称
        例如："锋利的玄铁重剑之吸血"
        
        Args:
            affixes: 词条列表
        
        Returns:
            tuple: (前缀, 后缀)
        """
        prefix_parts = []
        suffix_parts = []
        
        for affix in affixes:
            desc = affix.get('desc', '')
            if affix.get('type') == 'prefix':
                prefix_parts.append(desc)
            else:
                suffix_parts.append(desc)
        
        prefix = ''.join(prefix_parts)
        suffix = ''.join(suffix_parts)
        
        return prefix, suffix
    
    def get_affix_description(self, affixes):
        """
        获取词条的详细描述
        
        Args:
            affixes: 词条列表
        
        Returns:
            str: 描述文本
        """
        if not affixes:
            return ""
        
        lines = ["|y【词条】|n"]
        
        for i, affix in enumerate(affixes, 1):
            tier = affix.get('tier', 1)
            tier_color = self._get_tier_color(tier)
            
            # 词条名称
            affix_name = affix.get('id', '未知')
            lines.append(f"  {i}. {tier_color}{affix_name}|n (T{tier})")
            
            # 属性加成
            stats = affix.get('stats', {})
            if stats:
                stat_text = ", ".join([f"{k}+{v}" for k, v in stats.items()])
                lines.append(f"     {stat_text}")
            
            # 特殊效果
            effects = affix.get('effects', [])
            if effects:
                for effect in effects:
                    effect_type = effect.get('type', '未知')
                    lines.append(f"     效果: {effect_type}")
        
        return "\n".join(lines)
    
    def _get_tier_color(self, tier):
        """根据tier获取颜色"""
        colors = {
            1: "|w",  # 白色（普通）
            2: "|g",  # 绿色（优秀）
            3: "|b",  # 蓝色（稀有）
            4: "|m",  # 紫色（史诗）
            5: "|y",  # 黄色（传说）
        }
        return colors.get(tier, "|w")
    
    # ========== 词条管理 ==========
    
    def get_affix_by_id(self, affix_id):
        """
        通过ID获取词条模板
        
        Args:
            affix_id: 词条ID
        
        Returns:
            dict: 词条数据
        """
        for affix in self.affixes.values():
            if affix.get('id') == affix_id:
                return self._copy_affix(affix)
        return None
    
    def validate_affixes(self, affixes):
        """
        验证词条列表是否有效
        
        Args:
            affixes: 词条列表
        
        Returns:
            bool: 是否有效
        """
        if not isinstance(affixes, list):
            return False
        
        for affix in affixes:
            if not isinstance(affix, dict):
                return False
            if 'type' not in affix or affix['type'] not in ['prefix', 'suffix']:
                return False
        
        return True