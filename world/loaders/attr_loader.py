# world/loaders/attr_loader.py

import yaml
from django.conf import settings
import os

# 定义 YAML 路径
ATTR_FILE_PATH = os.path.join(settings.GAME_DIR, "data", "attributes.yaml")

class AttrLoader:
    """属性配置加载器"""
    
    _cache = None
    _last_mtime = 0

    @classmethod
    def load_attrs(cls, force_reload=False):
        """
        加载属性配置。
        支持热重载：如果文件修改过，会自动重新读取。
        """
        if not os.path.exists(ATTR_FILE_PATH):
            print(f"ERROR: 找不到属性配置文件: {ATTR_FILE_PATH}")
            return {}

        current_mtime = os.path.getmtime(ATTR_FILE_PATH)
        
        # 如果缓存存在且文件没变，直接返回缓存
        if cls._cache and not force_reload and current_mtime == cls._last_mtime:
            return cls._cache

        try:
            with open(ATTR_FILE_PATH, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                
            cls._cache = data
            cls._last_mtime = current_mtime
            print(f"|g[AttrLoader]|n 已加载属性配置，共 {len(data)} 条。")
            return data
            
        except Exception as e:
            print(f"|r[AttrLoader] 配置文件读取失败: {e}|n")
            return {}

    @classmethod
    def get_attr_config(cls, key):
        """获取单个属性的配置"""
        data = cls.load_attrs()
        return data.get(key, None)