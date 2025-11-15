# 魔法系统重构说明

## 新的文件结构

```
world/magic_new/
├── fire.yaml              # 火系基础属性
├── ice.yaml               # 冰系基础属性
├── fire/
│   ├── fireball.yaml      # 火球术完整定义
│   └── firewall.yaml      # 火墙术完整定义
├── ice/
│   ├── iceball.yaml       # 冰球术完整定义
│   └── iceblast.yaml      # 冰爆术完整定义
└── magic_index.json       # 魔法索引文件
```

## 设计理念

1. **顶层YAML文件** (`fire.yaml`, `ice.yaml`)：
   - 仅包含基础属性 (`_base`)
   - 不包含具体法术定义

2. **子目录中的独立YAML文件**：
   - 每个法术拥有独立的完整定义文件
   - 文件名与法术名一致

3. **魔法索引文件** (`magic_index.json`)：
   - 每个法术键名指向其独立的YAML文件
   - 路径采用相对路径格式

## 优势

1. **清晰的组织结构**：每个法术有独立文件，便于维护
2. **易于扩展**：添加新法术只需创建新文件并更新索引
3. **减少冲突**：多人协作时减少文件编辑冲突
4. **更好的可读性**：每个文件职责单一

## 使用方法

在代码中加载法术数据的方式保持不变：
```python
from typeclasses.spells.loader import load_spell_data

# 加载火球术数据
fireball_data = load_spell_data("fire.fireball")
```

系统会自动根据索引文件找到对应的独立YAML文件并加载数据。