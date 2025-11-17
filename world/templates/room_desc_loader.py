import os
import yaml
import random

class RoomDescTemplateLoader:
    _cache = {}

    @classmethod
    def _template_path(cls, name):
        return os.path.join(
            os.path.dirname(__file__),
            "rooms",
            "desc",
            f"{name}.yaml"
        )

    @classmethod
    def load(cls, name):
        if name in cls._cache:
            return cls._cache[name]
        
        path = cls._template_path(name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Template {name} not found at {path}")
            
        with open(path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            cls._cache[name] = data
            return data
    
    @classmethod
    def clear_cache(cls):
        """
        清除所有缓存
        """
        cls._cache.clear()

    @classmethod
    def get_room_description(cls, template_name):
        """
        从模板中获取房间描述，随机选择一个描述
        """
        try:
            data = cls.load(template_name)
            # 支持两种格式：带descriptions键的字典或直接的列表
            descriptions = []
            if isinstance(data, dict) and "descriptions" in data and isinstance(data["descriptions"], list):
                descriptions = data["descriptions"]
            elif isinstance(data, list):
                descriptions = data
                
            # 过滤掉空的描述
            descriptions = [desc for desc in descriptions if desc and str(desc).strip()]
            
            if descriptions:
                # 随机选择一个描述
                return random.choice(descriptions)
            return "这是一个房间。"
        except Exception:
            return "这是一个房间。"