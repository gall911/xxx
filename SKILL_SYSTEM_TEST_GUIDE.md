# 技能系统测试指南

## 1. 技能学习测试

### 学习火球术
```
learn fire.fireball
```

预期输出：
```
你学会了技能：fire.fireball
```

### 查看技能列表
```
skills
```

预期输出：
```
你已学会的技能：
- 火球术 (等级 1): 凝聚火焰向目标投出一枚火球。
```

## 2. 技能施放测试

### 创建测试目标
首先创建一个测试目标：
```
@py target = caller.search("测试木桩", quiet=True); 
if not target: 
    from evennia import create_object; 
    target = create_object("typeclasses.characters.Character", key="测试木桩", location=caller.location);
    target.db.hp = 100;
else:
    target = target[0];
    target.db.hp = 100;
caller.db.target = target;
caller.msg(f"目标{target.key}已创建，HP:{target.db.hp}")
```

### 设置攻击目标
```
hit 测试木桩
```

### 施放火球术
```
cast fire.fireball
```

预期输出：
```
你施放了火球术，对测试木桩造成50点伤害。
测试木桩对你施放了火球术，造成50点伤害。
```

检查目标HP：
```
@py caller.msg(f"目标HP: {caller.db.target.db.hp}")
```

预期输出：
```
目标HP: 50
```

## 3. 技能升级测试

### 提升技能等级
```
@py caller.db.skills["fire.fireball"]["level"] = 3
```

### 再次施放火球术
```
cast fire.fireball
```

预期输出：
```
你施放了火球术，对测试木桩造成70点伤害。
测试木桩对你施放了火球术，造成70点伤害。
```

检查目标HP：
```
@py caller.msg(f"目标HP: {caller.db.target.db.hp}")
```

预期输出：
```
目标HP: -20
```

## 4. 自动化测试

### 运行自动化测试脚本
```
@py import test.test_simple_fireball; test.test_simple_fireball.simple_test()
```

预期输出：
```
角色消息: 你施放了火球术，对测试木桩造成70点伤害。
目标消息: _TestCaller对你施放了火球术，造成70点伤害。
目标剩余HP: 30
清理目标: 测试木桩
```

## 5. 文件结构验证

### 技能配置文件
- `world/magic/magic_index.json` - 技能索引
- `world/magic/fire/fireball.json` - 火球术配置

### 核心代码文件
- `typeclasses/spells/spell_base.py` - 技能基类
- `typeclasses/spells/loader.py` - 技能加载器
- `commands/cast.py` - 施法命令
- `commands/skill_learn.py` - 学习技能命令
- `commands/skills.py` - 技能列表命令

### 测试文件
- `test/test_simple_fireball.py` - 火球术测试脚本
- `test/README.md` - 测试说明文档

## 6. 技能系统特点

1. **极简设计**：技能逻辑尽可能简单，复杂功能通过扩展实现
2. **数据驱动**：技能配置完全由JSON文件控制
3. **易于扩展**：添加新技能只需创建JSON配置文件并在索引中注册
4. **灵活升级**：技能等级直接影响伤害计算
5. **低耦合**：技能系统与游戏其他系统解耦

## 7. 技能伤害计算公式

```
伤害 = 基础伤害 + 每级增量 × (技能等级 - 1)
```

例如：
- 火球术基础伤害：50
- 每级增量：10
- 1级火球术伤害：50 + 10 × (1-1) = 50
- 3级火球术伤害：50 + 10 × (3-1) = 70