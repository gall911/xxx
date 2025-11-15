# YAML技能系统使用说明

## 概述

这个技能系统支持YAML格式的技能配置文件，相比JSON格式，YAML更适合编写多行文本和复杂的技能描述。

## 技能配置格式

### YAML格式示例

```yaml
name: 火球术
type: damage
damage:
  base: 50
  per_level: 10
mp_cost: 20
cast_time: 2
cooldown: 5
range: 10
desc: |
  凝聚火焰向目标投出一枚火球。
  这是一个强大的火系技能，能够对敌人造成大量伤害。
  随着技能等级提升，伤害也会增加。
```

### JSON格式示例（旧格式）

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

## YAML格式优势

1. **多行文本支持**：使用`|`符号可以轻松编写多行技能描述
2. **更易读**：YAML格式比JSON更简洁易读
3. **更好的注释支持**：可以使用`#`添加注释
4. **灵活性**：支持更复杂的数据结构

## 使用方法

### 1. 创建新的YAML技能文件

在`world/magic/`目录下创建YAML文件，例如`fire/fireball.yaml`：

```yaml
name: 火球术
type: damage
damage:
  base: 50
  per_level: 10
mp_cost: 20
cast_time: 2
cooldown: 5
range: 10
desc: |
  凝聚火焰向目标投出一枚火球。
  这是一个强大的火系技能，能够对敌人造成大量伤害。
  随着技能等级提升，伤害也会增加。
```

### 2. 更新索引文件

在`world/magic/magic_index.json`中添加或更新技能映射：

```json
{
    "fire.fireball": "fire/fireball.yaml",
    "fire.firewall": "fire/firewall.yaml"
}
```

### 3. 转换现有JSON文件

运行转换脚本将所有JSON文件转换为YAML格式：

```bash
python convert_json_to_yaml.py
```

## 安装依赖

YAML支持需要安装PyYAML库：

```bash
pip install PyYAML
```

## 技能配置字段说明

- `name`: 技能名称
- `type`: 技能类型
- `damage`: 伤害配置
  - `base`: 基础伤害
  - `per_level`: 每级伤害加成
- `mp_cost`: MP消耗
- `cast_time`: 吟唱时间（秒）
- `cooldown`: 冷却时间（秒）
- `range`: 施法距离
- `desc`: 技能描述（支持多行文本）

## 注意事项

1. 系统同时支持JSON和YAML格式，可以混合使用
2. YAML文件扩展名必须是`.yaml`或`.yml`
3. 技能索引文件中需要正确指向YAML文件路径
4. 确保安装了PyYAML库以支持YAML格式