# 木桩NPC创建和使用说明

## 创建木桩NPC

您可以使用现有的 `create_npc` 命令来创建木桩NPC。

### 使用方法

在游戏内输入以下命令创建木桩NPC：

```
create_npc 木桩 = invincible, english_name:mz, display_name:木桩（mz）
```

这将创建一个位于您当前位置的木桩NPC，具有以下特性：
- 显示名称：木桩（mz）
- 英文别名：mz
- 无敌状态：是（不会被杀死）
- 初始HP：100

### 使用场景

这个木桩NPC可以用于：
1. 测试战斗技能
2. 作为装饰性对象
3. 任务目标标记

## 一般NPC创建命令

您可以使用通用的NPC创建命令来创建各种NPC：

```
create_npc <名字> [= invincible] [= english_name:<英文名>] [= display_name:<显示名称>]
```

示例：
```
create_npc 僵尸 = invincible, english_name:zombie, display_name:无敌僵尸（zombie）
```

## 操作木桩NPC

创建后，您可以像操作其他对象一样操作木桩NPC：
- 使用 `look mz` 或 `look 木桩` 查看
- 使用 `hit mz` 或 `hit 木桩` 进行攻击测试
- 使用 `teach mz <技能>` 教授技能（如果支持）

## 注意事项

1. 木桩NPC默认是无敌的，不会被普通攻击杀死
2. 木桩NPC的位置是创建时您所在的位置
3. 如需删除木桩NPC，可以使用 `destroy mz` 命令