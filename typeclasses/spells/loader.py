import json, os
from utils.json_cache import load_json

MAGIC_ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "world", "magic")
INDEX_FILE = os.path.join(MAGIC_ROOT, "magic_index.json")

# 加载魔法索引
MAGIC_INDEX = {}
if os.path.exists(INDEX_FILE):
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        MAGIC_INDEX = json.load(f)

def load_spell_data(spell_key):
    """Load spell data by its key."""
    # 直接找
    if spell_key in MAGIC_INDEX:
        file_path = MAGIC_INDEX[spell_key]
    else:
        # 后缀匹配，例如 iceball -> ice.iceball
        matched_key = None
        for k in MAGIC_INDEX.keys():
            if k.endswith("." + spell_key) or k == spell_key:
                matched_key = k
                break
        if not matched_key:
            return None
        file_path = MAGIC_INDEX[matched_key]

    # 处理路径
    import os
    if not os.path.isabs(file_path):
        from typeclasses.spells.loader import MAGIC_ROOT
        file_path = os.path.join(MAGIC_ROOT, file_path)

    if file_path.endswith(".yaml"):
        import yaml
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    else:
        from utils.json_cache import load_json
        return load_json(file_path)
