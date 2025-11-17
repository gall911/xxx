import json
import os

# 尝试导入yaml模块，如果不存在则只支持JSON
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

_cache = {}

def load_data(path):
    """
    加载数据文件，支持JSON和YAML格式
    """
    if path in _cache:
        return _cache[path]
    
    # 根据文件扩展名确定格式
    if path.endswith('.yaml') or path.endswith('.yml'):
        if not YAML_AVAILABLE:
            raise ImportError("YAML support not available. Please install PyYAML.")
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
    else:
        # 默认为JSON格式
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    
    _cache[path] = data
    return data

def clear_cache():
    """
    清空缓存
    """
    global _cache
    _cache = {}