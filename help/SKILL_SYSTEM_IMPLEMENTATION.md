# 技能系统实现说明

## 设计理念

按照文档要求，我们的技能系统采用极简设计原则：
1. 技能数据全部存储在JSON文件中
2. Python代码只负责加载和执行逻辑
3. 技能基类尽可能简单
4. cast命令只处理最基本的施法流程

## 目录结构

```
world/magic/
├── magic_index.json     # 技能索引文件
├── fire/
│   ├── fireball.json    # 火球术配置
│   └── firewall.json    # 火墙术配置
├── ice/
│   └── iceblast.json    # 冰爆术配置
└── sword/
    └── slash.json       # 斩击配置

typeclasses/spells/
├── spell_base.py        # 技能基类
└── loader.py            # 技能加载器

commands/
├── cast.py              # 施法命令
├── skill_learn.py       # 学习技能命令
└── skills.py            # 查看技能列表命令
```

## 核心组件

### 1. 技能索引文件 (magic_index.json)

```json
{
    "fire.fireball": "fire/fireball.json",
    "fire.firewall": "fire/firewall.json",
    "ice.iceblast": "ice/iceblast.json",
    "sword.slash": "sword/slash.json"
}
```

### 2. 技能配置文件 (fire/fireball.json)

```json
{
    "name": "火球术",
    "type": "damage",
    "damage": {
        "base": 50,
        "per_level": 10
    },
    "mp_cost": 20,
    "cast_time": 2,
    "cooldown": 5,
    "range": 10,
    "desc": "凝聚火焰向目标投出一枚火球。"
}
```

### 3. 技能基类 (spell_base.py)

```python
class Spell:
    def __init__(self, caster, data):
        self.caster = caster
        self.data = data
```

### 4. 技能加载器 (loader.py)

```python
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
```

### 5. 施法命令 (cast.py)

```python
from evennia import Command
from typeclasses.spells.loader import load_spell_data
from typeclasses.spells.spell_base import Spell

class CmdCast(Command):
    key = "cast"
    locks = "cmd:all()"

    def func(self):
        if not self.args:
            self.caller.msg("施放什么技能？")
            return
            
        spell_key = self.args.strip().lower()

        # 判断是否已学会
        if not hasattr(self.caller.db, 'skills') or spell_key not in self.caller.db.skills:
            self.caller.msg("你没有学会这个技能。")
            return

        # 加载 JSON 数据
        data = load_spell_data(spell_key)
        if not data:
            self.caller.msg("技能不存在。")
            return

        # 获取目标
        target = self.caller.db.target if hasattr(self.caller.db, 'target') else None
        if not target:
            self.caller.msg("你没有指定目标。")
            return

        # 创建技能对象
        spell = Spell(self.caller, data)

        # 计算伤害
        skill_level = self.caller.db.skills[spell_key]["level"]
        dmg = data["damage"]["base"] + data["damage"]["per_level"] * (skill_level - 1)

        # 应用伤害
        target.db.hp -= dmg

        # 发送消息
        self.caller.msg(f"你施放了{data['name']}，对{target.key}造成{dmg}点伤害。")
        target.msg(f"{self.caller.key}对你施放了{data['name']}，造成{dmg}点伤害。")
```

## 角色技能存储格式

角色学会的技能存储在 `character.db.skills` 中：

```python
{
    "fire.fireball": {"level": 1},
    "ice.iceblast": {"level": 3}
}
```

## 使用方法

1. 学习技能：
   ```
   learn fire.fireball
   ```

2. 查看技能列表：
   ```
   skills
   ```

3. 设置攻击目标：
   ```
   hit <目标名>
   ```

4. 施放技能：
   ```
   cast fire.fireball
   ```

## 测试方法

运行测试脚本：
```
@py import test.test_simple_fireball; test.test_simple_fireball.simple_test()
```