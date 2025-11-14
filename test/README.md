# 测试目录

这里包含了各种测试脚本。

## 测试脚本列表

- `test_cmdset.py` - CmdSet测试
- `test_exit_search.py` - Exit搜索测试
- `test_fireball.py` - 火球术完整测试
- `test_fireball_quick.py` - 火球术快速测试
- `test_fireball_in_game.py` - 游戏内火球术测试
- `test_simple_fireball.py` - 火球术最简测试
- `test_skills.py` - 技能系统测试
- `test_in_game.py` - 完整技能系统游戏内测试
- `test_comprehensive.py` - 技能系统综合测试
- `test_comprehensive_updated.py` - 更新版技能系统综合测试
- `test_commands_simple.py` - 简单命令测试
- `test_commands_standalone.py` - 独立命令测试
- `test_skill_system.py` - 技能系统测试入口

## 技能系统测试说明

### 游戏内测试方法

#### 完整技能系统测试（推荐）

```
@py import test.test_in_game; test.test_in_game.test_skill_system_in_game(self)
```

或者使用简短别名：

```
@py import test.test_in_game as t; t.test(self)
```

#### 火球术专项测试

运行以下命令进行游戏内测试：

```
@py import test.test_fireball_in_game; test.test_fireball_in_game.test_fireball()
```

或者使用简短别名：

```
@py import test.test_fireball_in_game as fb; fb.run()
```

### 最简测试方法

运行以下命令进行最简测试：

```
@py import test.test_simple_fireball; test.test_simple_fireball.simple_test()
```

这个测试会：
1. 创建一个3级火球术技能
2. 创建一个100HP的测试目标
3. 设置目标并施放火球术
4. 显示目标剩余HP（应为30HP，因为3级火球术伤害为50+(3-1)*10=70）
5. 清理测试目标

### 综合功能测试

运行以下命令进行综合功能测试：

```
@py import test.test_comprehensive; test.test_comprehensive.run_comprehensive_test()
```

### 手动测试方法

1. 学习火球术：
   ```
   learn fire.fireball
   ```

2. 创建一个测试目标或者找到一个NPC

3. 设置攻击目标：
   ```
   hit <目标名>
   ```

4. 施放火球术：
   ```
   cast fire.fireball
   ```

5. 查看目标的HP变化

火球术的基础伤害是50，每级增加10点伤害：
- 1级火球术：50点伤害
- 3级火球术：70点伤害