import json

_cache = {}

def load_json(path):
    if path in _cache:
        return _cache[path]
    with open(path) as f:
        data = json.load(f)
    _cache[path] = data
    return data