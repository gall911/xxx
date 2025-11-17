import os
import yaml
from collections import defaultdict

class TemplateLoader:
    _cache = {}

    @classmethod
    def _template_path(cls, name):
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
            raise FileNotFoundError(f"Template {name} not found at {path}")
            
        with open(path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            cls._cache[name] = data
            return data

    @classmethod
    def apply_to_character(cls, character, template_name):
        data = cls.load(template_name)
        
        # Apply basic attributes
        for key, value in data.get('attributes', {}).items():
            setattr(character, key, value)
            
        # Apply stats
        for key, value in data.get('stats', {}).items():
            if hasattr(character, key):
                setattr(character, key, value)
                
        # Apply skills
        skills = data.get('skills', {})
        if skills and hasattr(character, 'skills'):
            for skill_name, skill_data in skills.items():
                character.skills.add(skill_name, **skill_data)