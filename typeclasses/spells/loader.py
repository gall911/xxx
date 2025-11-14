import json, os
from utils.json_cache import load_json

MAGIC_ROOT = "world/magic/"
INDEX_FILE = os.path.join(MAGIC_ROOT, "magic_index.json")

with open(INDEX_FILE) as f:
    MAGIC_INDEX = json.load(f)

def load_spell_data(spell_key):
    if spell_key not in MAGIC_INDEX:
        return None
    file_path = os.path.join(MAGIC_ROOT, MAGIC_INDEX[spell_key])
    return load_json(file_path)

def get_spell_key_by_name(spell_name):
    """通过技能名称查找技能键名"""
    for key, file_path in MAGIC_INDEX.items():
        full_path = os.path.join(MAGIC_ROOT, file_path)
        spell_data = load_json(full_path)
        if spell_data and spell_data.get('name') == spell_name:
            return key
    return None