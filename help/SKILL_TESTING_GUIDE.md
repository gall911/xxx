# 技能系统测试说明

## 1. 手动测试步骤

### 1.1 学习技能
```
learn fire.fireball
```

### 1.2 查看技能列表
```
skills
```

### 1.3 创建测试目标
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

### 1.4 设置攻击目标
```
hit 测试木桩
```

### 1.5 施放技能
```
cast fire.fireball
```

### 1.6 检查结果
```
@py caller.msg(f"目标HP: {caller.db.target.db.hp}")
```

## 2. 自动化测试

### 2.1 游戏内测试脚本
```
@py import test.test_fireball_in_game; test.test_fireball_in_game.test_fireball()
```

### 2.2 简单测试脚本
```
@py import test.test_simple_fireball; test.test_simple_fireball.simple_test()
```

## 3. 预期结果

### 3.1 1级火球术
- 基础伤害: 50
- 目标HP减少: 50

### 3.2 3级火球术
- 基础伤害: 50
- 每级增量: 10
- 3级伤害: 50 + 10 × (3-1) = 70
- 目标HP减少: 70

## 4. 技能系统组件

### 4.1 技能配置文件
- `world/magic/magic_index.json` - 技能索引
- `world/magic/fire/fireball.json` - 火球术配置

### 4.2 核心代码
- `typeclasses/spells/spell_base.py` - 技能基类
- `typeclasses/spells/loader.py` - 技能加载器
- `commands/cast.py` - 施法命令
- `commands/skill_learn.py` - 学习技能命令
- `commands/skills.py` - 技能列表命令

## 5. 故障排除

### 5.1 技能不存在
检查技能是否在 `magic_index.json` 中正确注册。

### 5.2 技能配置加载失败
检查JSON文件格式是否正确。

### 5.3 目标未设置
确保使用 `hit` 命令设置了攻击目标。

### 5.4 技能未学习
使用 `learn` 命令学习技能后再施放。