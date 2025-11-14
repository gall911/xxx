# 技能系统使用说明

## 概述

这是一个基于JSON配置的技能系统，允许通过简单的JSON文件定义技能，而无需编写Python代码。

## 基本命令

- `cast <技能名>` - 施放技能
- `hit <目标>` - 设置攻击目标
- `learn <技能名>` - 学习新技能
- `skills` - 查看已学会的技能

## 技能配置

技能定义在 `world/magic/` 目录下的JSON文件中。每个技能包含以下属性：

```json
{
    "name": "技能名称",
    "type": "技能类型",
    "damage": {
        "base": 基础伤害,
        "per_level": 每级加成
    },
    "mp_cost": MP消耗,
    "cast_time": 吟唱时间,
    "cooldown": 冷却时间,
    "range": 施法距离,
    "desc": "技能描述"
}
```

## 添加新技能

1. 在 `world/magic/` 目录下创建新的JSON文件
2. 在 `world/magic/magic_index.json` 中添加技能索引
3. 重新加载游戏或使用 `reload` 命令

## 技能类型

目前支持的技能类型：
- `damage` - 伤害技能

## 示例

```
# 学习火球术
learn fire.fireball

# 设置目标
hit 测试木桩

# 施放技能
cast fire.fireball

# 查看技能列表
skills
```

## 测试

使用测试脚本进行技能系统测试：

```
@py import test.test_skills; test.test_skills.setup_test_character()
@py import test.test_skills; test.test_skills.test_skills()
```