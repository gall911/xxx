# world/systems/attr_manager.py
"""
属性管理器 - 修改属性的唯一入口
负责: 属性初始化、修改、查询、境界数值应用
"""

from world.loaders.attr_loader import AttrLoader
from world.loaders.game_data import get_data


class AttrManager:
    """
    属性管理器
    
    核心原则: 所有属性修改必须通过这里进行
    禁止直接修改 character.db.* 或 character.attributes.*
    """
    
    # ========== 初始化相关 ==========
    
    @staticmethod
    def init_attributes(character):
        """
        根据 attributes.yaml 初始化角色属性
        通常在 at_object_creation 调用
        
        Args:
            character: 角色对象
        """
        configs = AttrLoader.load_attrs()
        
        for key, info in configs.items():
            attr_type = info.get('type', 'string')
            default_val = info.get('default', None)
            base_val = info.get('base', None)
            
            # Gauge 类型 (HP, Qi) -> 需要存当前值和最大值
            if attr_type == 'gauge':
                max_key = f"max_{key}"
                
                if not character.attributes.has(max_key):
                    character.attributes.add(max_key, base_val or 0)
                
                if not character.attributes.has(key):
                    character.attributes.add(key, base_val or 0)
            
            # 其他类型 (Int, Float, Dict, List)
            else:
                if not character.attributes.has(key):
                    character.attributes.add(key, default_val)
    
    @staticmethod
    def apply_realm_stats(character):
        """
        应用境界的基础属性
        
        在以下情况调用:
        - 角色创建时
        - 突破境界时
        
        Args:
            character: 角色对象
        """
        realm_name = character.db.realm
        realm_data = get_data('realms', realm_name)
        
        if not realm_data:
            print(f"[AttrManager] 警告: 找不到境界数据 '{realm_name}'")
            return
        
        # 获取基础属性
        base_stats = realm_data.get('base_stats', {})
        
        # 覆盖基础属性
        for key, value in base_stats.items():
            # 只有当属性在 attributes.yaml 里定义过才写入
            if character.attributes.has(key) or key.startswith('max_'):
                character.attributes.add(key, value)
        
        # 同步到内存
        character.sync_stats_to_ndb()
    
    @staticmethod
    def apply_level_growth(character):
        """
        应用等级成长属性
        
        计算公式: 总属性 = 基础值 + (等级-1) × 每级成长
        
        在以下情况调用:
        - 角色创建后 (计算初始属性)
        - 升级后 (重新计算)
        
        Args:
            character: 角色对象
        """
        realm_name = character.db.realm
        realm_data = get_data('realms', realm_name)
        
        if not realm_data:
            return
        
        level = character.db.level or 1
        base_stats = realm_data.get('base_stats', {})
        level_growth = realm_data.get('level_growth', {})
        
        # 计算该等级应有的总属性值
        for attr, per_level in level_growth.items():
            base_value = base_stats.get(attr, 0)
            total_value = base_value + (level - 1) * per_level
            character.attributes.add(attr, total_value)
        
        # 同步到内存
        character.sync_stats_to_ndb()
    
    # ========== 属性修改相关 ==========
    
    @staticmethod
    def set_attr(character, attr_name, value):
        """
        设置属性值 (绝对值)
        
        ✅ 正确写法:
            AttrManager.set_attr(char, 'strength', 100)
        
        ❌ 错误写法:
            char.db.strength = 100  # 禁止!
        
        Args:
            character: 角色对象
            attr_name: 属性名 (建议使用 At.STRENGTH 常量)
            value: 新值
        """
        # 验证属性名
        config = AttrLoader.get_attr_config(attr_name)
        if not config and not attr_name.startswith('max_'):
            print(f"[AttrManager] 警告: 未知属性 '{attr_name}'")
        
        # 写入数据库
        character.attributes.add(attr_name, value)
        
        # 同步到内存
        character.sync_stats_to_ndb()
    
    @staticmethod
    def modify_attr(character, attr_name, delta):
        """
        修改属性值 (相对值)
        
        例如: 升级加 strength +5
        
        Args:
            character: 角色对象
            attr_name: 属性名
            delta: 变化值 (可正可负)
        """
        current = character.attributes.get(attr_name) or 0
        AttrManager.set_attr(character, attr_name, current + delta)
    
    @staticmethod
    def get_attr(character, attr_name):
        """
        获取属性值 (含装备加成)
        
        优先从内存读取 (ndb)，因为已包含装备加成
        
        Args:
            character: 角色对象
            attr_name: 属性名
        
        Returns:
            属性值
        """
        # 优先从内存读 (包含装备加成)
        value = getattr(character.ndb, attr_name, None)
        
        if value is not None:
            return value
        
        # 内存没有，从数据库读
        return character.attributes.get(attr_name) or 0
    
    @staticmethod
    def get_base_attr(character, attr_name):
        """
        获取基础属性值 (不含装备加成)
        
        直接从数据库读取
        
        Args:
            character: 角色对象
            attr_name: 属性名
        
        Returns:
            基础属性值
        """
        return character.attributes.get(attr_name) or 0
    
    # ========== 元数据查询 ==========
    
    @staticmethod
    def get_name(key):
        """
        获取属性显示名称
        
        例: 'strength' -> '臂力'
        
        Args:
            key: 属性key
        
        Returns:
            str: 显示名称
        """
        config = AttrLoader.get_attr_config(key)
        if config:
            return config.get('name', key)
        
        # 处理 max_* 类型
        if key.startswith('max_'):
            base_key = key[4:]  # 去掉 'max_'
            base_config = AttrLoader.get_attr_config(base_key)
            if base_config:
                return base_config.get('name', base_key) + '上限'
        
        return key
    
    @staticmethod
    def get_desc(key):
        """
        获取属性描述
        
        Args:
            key: 属性key
        
        Returns:
            str: 描述文本
        """
        config = AttrLoader.get_attr_config(key)
        if config:
            return config.get('desc', "")
        return ""
    
    @staticmethod
    def get_category(key):
        """
        获取属性分类
        
        Args:
            key: 属性key
        
        Returns:
            str: 分类名称 ('combat', 'cultivation', 'hidden', etc.)
        """
        config = AttrLoader.get_attr_config(key)
        if config:
            return config.get('category', 'misc')
        return 'misc'
    
    # ========== 调试工具 ==========
    
    @staticmethod
    def dump_attributes(character):
        """
        导出角色所有属性 (调试用)
        
        Args:
            character: 角色对象
        
        Returns:
            dict: 属性字典
        """
        attrs = {}
        
        # 从数据库读取所有属性
        for attr_obj in character.attributes.all():
            attrs[attr_obj.key] = attr_obj.value
        
        return attrs
    
    @staticmethod
    def validate_attributes(character):
        """
        验证角色属性完整性 (调试用)
        
        检查:
        - 是否所有必需属性都存在
        - 数值是否合法
        
        Args:
            character: 角色对象
        
        Returns:
            tuple: (是否通过, 错误列表)
        """
        errors = []
        configs = AttrLoader.load_attrs()
        
        for key, info in configs.items():
            attr_type = info.get('type')
            
            if attr_type == 'gauge':
                # 检查 max_* 和当前值
                max_key = f"max_{key}"
                
                if not character.attributes.has(max_key):
                    errors.append(f"缺少属性: {max_key}")
                
                if not character.attributes.has(key):
                    errors.append(f"缺少属性: {key}")
                else:
                    # 检查当前值是否超过最大值
                    current = character.attributes.get(key) or 0
                    max_val = character.attributes.get(max_key) or 0
                    
                    if current > max_val:
                        errors.append(f"{key} 超过上限: {current}/{max_val}")
            
            else:
                if not character.attributes.has(key):
                    errors.append(f"缺少属性: {key}")
        
        return len(errors) == 0, errors