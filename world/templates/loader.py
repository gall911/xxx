import os
import yaml
from evennia.utils import logger

class TemplateLoader:

    _cache = {}
    max_cache_size = 200

    @classmethod
    def _template_path(cls, name):
        # 正确且通用
        return os.path.join(
            os.path.dirname(__file__),
            "character",
            f"{name}.yaml"
        )

    @classmethod
    def load(cls, name):
        if name in cls._cache:
            return cls._cache[name]

        path = cls._template_path(name)
        if not os.path.exists(path):
            logger.log_err(f"Template file not found: {path}")
            return {}

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        if len(cls._cache) >= cls.max_cache_size:
            cls._cache.clear()  # 简单粗暴但安全

        cls._cache[name] = data
        return data

    @classmethod
    def apply_to_character(cls, obj, template_name):
        data = cls.load(template_name)
        for key, value in data.items():
            setattr(obj.db, key, value)
