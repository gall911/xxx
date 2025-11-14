# 技能系统

这是一个基于JSON配置的极简技能系统，允许通过简单的JSON文件定义技能，而无需编写Python代码。

## 快速开始

### 学习技能
```
learn fire.fireball
```

### 查看技能
```
skills
```

### 设置目标
```
hit <目标名>
```

### 施放技能
```
cast fire.fireball
```

## 文档

- [技能系统使用说明](SKILL_SYSTEM_README.md) - 用户使用指南
- [技能系统实现说明](SKILL_SYSTEM_IMPLEMENTATION.md) - 技术实现细节
- [技能系统测试指南](SKILL_SYSTEM_TEST_GUIDE.md) - 测试方法和步骤
- [技能系统验证报告](SKILL_SYSTEM_VALIDATION_REPORT.md) - 测试验证结果
- [技能系统最终总结](SKILL_SYSTEM_FINAL_SUMMARY.md) - 项目最终总结

## 核心特性

1. **数据驱动**：所有技能数据存储在JSON文件中
2. **极易扩展**：添加新技能只需创建JSON配置文件
3. **等级系统**：技能等级影响伤害计算
4. **解耦设计**：技能系统与游戏其他部分低耦合

## 文件结构

```
commands/                 # 技能相关命令
typeclasses/spells/       # 技能基类和加载器
world/magic/              # 技能配置文件
test/                     # 测试脚本
```

## 测试

在游戏内运行完整测试：
```
@py import test.test_in_game; test.test_in_game.test_skill_system_in_game(self)
```