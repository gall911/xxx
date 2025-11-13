# MUD游戏配置系统

这是一个为MUD游戏设计的完整配置系统，包括配置文件结构、缓存机制、验证功能、版本控制和热更新功能。

## 项目结构

```
项目根目录/
├── config_system/           # 配置系统模块
│   ├── __init__.py         # 模块初始化文件
│   ├── config_loader.py    # 配置加载器核心实现
│   ├── validator.py        # 配置验证模块
│   ├── version_manager.py  # 配置版本控制模块
│   └── example.py          # 使用示例
├── configs/                # 配置文件目录
│   ├── basic/              # 基础配置
│   │   ├── attributes.yaml # 角色属性配置
│   │   └── realms.yaml     # 修炼境界配置
│   ├── items/              # 物品配置
│   │   ├── weapons.yaml    # 武器配置
│   │   └── armors.yaml     # 护甲配置
│   ├── npcs/               # NPC配置
│   │   └── merchants.yaml  # 商人配置
│   └── systems/            # 系统配置
│       └── combat.yaml     # 战斗系统配置
├── config_versions/        # 配置版本存储目录（默认）
├── config_daemon.py        # 配置守护进程脚本
├── game_integration_example.py  # 游戏集成示例
├── character_attributes_example.py # 角色属性系统示例
├── setup_attribute_validation.py # 属性验证规则设置脚本
├── run_config_example.py   # 配置示例启动脚本
├── CONFIG_USAGE.md         # 详细使用指南
```

## 实际使用指南

### 基本使用流程

1. **配置您的游戏参数**
   编辑 `configs/` 目录下的YAML文件，设置游戏参数

2. **集成到您的游戏**
   ```python
   from config_system import get_config_loader
   
   # 获取配置加载器
   loader = get_config_loader(
       enable_validation=True,
       enable_version_control=True
   )
   
   # 获取配置
   combat_config = loader.get_config("systems/combat")
   attributes_config = loader.get_config("basic/attributes")
   ```

3. **设置配置验证规则**
   ```python
   # 添加验证规则
   loader.add_validation_rule(
       "systems/combat", 
       "base_hit_rate", 
       "range", 
       min_val=0.0, 
       max_val=1.0
   )
   
   # 验证配置
   errors = loader.validate_config("systems/combat")
   if errors:
       for error in errors:
           print(f"验证错误: {error}")
   ```

4. **处理配置更新**
   ```python
   # 注册配置更新回调
   def on_config_updated(config_name, config_content):
       print(f"配置 {config_name} 已更新")
       # 在这里处理配置更新逻辑
   
   loader.register_update_callback(on_config_updated)
   ```

### 生产环境部署

对于生产环境，建议使用守护进程模式：

```bash
# 启动配置守护进程
python config_daemon.py start

# 检查状态
python config_daemon.py status

# 停止守护进程
python config_daemon.py stop
```

### 常见使用场景

1. **调整游戏平衡性**
   - 修改战斗系统参数
   - 调整物品属性
   - 重新平衡角色属性

2. **添加新内容**
   - 添加新物品
   - 创建新NPC
   - 扩展游戏系统

3. **A/B测试**
   - 保存多个配置版本
   - 在不同服务器上使用不同配置
   - 比较不同配置的效果

4. **回滚错误配置**
   - 当配置错误导致问题时
   - 快速恢复到之前的稳定版本




│   ├── classes.yaml        # 职业分类与特性
│   └── constants.yaml      # 游戏常量配置
├── spells/                 # 法术系统
│   ├── categories.yaml     # 法术类别定义
│   ├── attack.yaml         # 攻击类法术
│   ├── support.yaml        # 辅助类法术
│   └── special.yaml        # 特殊类法术
├── items/                  # 物品系统
│   ├── weapons.yaml        # 各种武器配置
│   ├── armors.yaml         # 各种防具配置
│   ├── pills.yaml          # 各种丹药配置
│   ├── materials.yaml      # 炼器/炼丹材料
│   └── special.yaml        # 任务物品等特殊物品
├── npcs/                   # NPC系统
│   ├── merchants.yaml      # 商铺NPC
│   ├── guards.yaml         # 城镇守卫
│   ├── quest_givers.yaml   # 发布/完成任务的NPC
│   └── monsters.yaml       # 野外怪物
├── maps/                   # 地图系统
│   ├── areas.yaml          # 大区域配置
│   ├── rooms.yaml          # 具体房间配置
│   ├── portals.yaml        # 传送点配置
│   └── events.yaml         # 地图相关事件
├── quests/                 # 任务系统
│   ├── main.yaml           # 主线任务配置
│   ├── side.yaml           # 支线任务配置
│   ├── daily.yaml          # 日常任务配置
│   └── rewards.yaml        # 任务奖励配置
├── systems/                # 系统设置
│   ├── experience.yaml     # 经验获取与升级
│   ├── combat.yaml         # 战斗系统设置
│   ├── economy.yaml        # 游戏经济系统
│   └── social.yaml         # 师徒、帮派等社交系统
└── yaml_advanced_examples.yaml  # YAML高级特性示例
```

## 安装依赖

首先，确保您已经安装了所需的依赖包：

```bash
pip install -r requirements.txt
```

如果您没有 requirements.txt 文件，可以直接安装所需依赖：

```bash
pip install PyYAML watchdog
```

## 新功能

### 配置验证功能

配置验证功能允许您定义规则来验证配置文件的内容，确保配置值符合预期的格式、类型和取值范围。

```python
# 添加验证规则
loader.add_validation_rule("systems/combat", "base_hit_rate", "type", expected_type="float")
loader.add_validation_rule("systems/combat", "base_hit_rate", "range", min_val=0.0, max_val=1.0)

# 验证配置
errors = loader.validate_config("systems/combat")
if errors:
    for error in errors:
        print(f"验证错误: {error}")
```

### 配置版本控制功能

配置版本控制功能允许您保存配置的历史版本，比较版本差异，并恢复到之前的版本。

#### 自动版本保存

配置系统会在以下情况自动保存版本：
- 初始加载配置时
- 重新加载配置时

#### 手动版本管理

```python
# 获取当前配置
config_data = loader.get_config("basic/attributes")

# 手动保存版本（带描述）
if loader.enable_version_control and loader.version_manager:
    loader.version_manager.save_version(
        "basic/attributes", 
        config_data, 
        "手动保存的版本"
    )

# 列出配置的所有版本
versions = loader.list_config_versions("systems/combat")
for version in versions:
    print(f"版本 {version['version_id']}: {version['description']} ({version['datetime']})")

# 恢复到指定版本
if versions:
    loader.restore_config_version("systems/combat", versions[0]["version_id"])

# 比较两个版本
if len(versions) >= 2:
    diff = loader.compare_config_versions("systems/combat", versions[0]["version_id"], versions[1]["version_id"])
    print("版本差异:")
    for change in diff["differences"]:
        print(f"  {change['path']}: {change['type']}")
```

#### 版本存储目录

默认情况下，配置版本存储在 `config_versions` 目录中，按配置文件组织：

```
config_versions/
├── basic/
│   ├── attributes_123456789.json
│   └── realms_123456790.json
├── systems/
│   └── combat_123456791.json
└── npcs/
    └── merchants_123456792.json
```

您可以通过以下方式自定义版本存储目录：

```python
# 获取配置加载器，自定义版本目录
loader = get_config_loader(
    config_dir="configs",
    versions_dir="config_system/versions"  # 自定义版本目录
)
```

### 守护进程模式

守护进程模式允许配置系统作为后台服务运行，持续监视配置文件变化，无需占用终端窗口。

```bash
# 启动配置守护进程
python config_daemon.py start

# 检查状态
python config_daemon.py status

# 停止守护进程
python config_daemon.py stop
```

## 角色属性系统

角色属性系统提供了完整的角色属性定义、计算和修正功能，包括基础属性、衍生属性、种族和职业修正等。

### 属性配置文件

角色属性配置位于 `configs/basic/attributes.yaml`，包含以下部分：

1. **基础属性定义**：定义力量、敏捷、体质等基础属性
2. **属性计算公式**：定义生命值、法力值等衍生属性的计算公式
3. **属性点分配系统**：定义属性点分配规则
4. **种族属性修正**：定义不同种族的属性修正
5. **职业属性修正**：定义不同职业的属性修正

### 使用示例

```python
from config_system import get_config_loader

# 获取配置加载器
loader = get_config_loader()

# 获取角色属性配置
attributes_config = loader.get_config("basic/attributes")

# 获取力量属性定义
strength_data = attributes_config["attributes"]["strength"]
print(f"力量: {strength_data['name']} - {strength_data['description']}")

# 获取生命值计算公式
health_formula = attributes_config["formulas"]["health"]["formula"]
print(f"生命值计算公式: {health_formula}")
```

### 运行示例

```bash
# 运行角色属性示例
python character_attributes_example.py

# 设置角色属性验证规则
python setup_attribute_validation.py
```

## 使用方法

### 基本用法

```python
from config_system import get_config_loader

# 获取配置加载器实例
loader = get_config_loader()

# 获取整个配置文件
attributes_config = loader.get_config("basic/attributes")

# 获取配置中的特定值
base_hit_rate = loader.get_value("systems/combat", "base_hit_rate", 0.9)
```

### 配置热更新

```python
def on_config_update(config_name, config_content):
    """配置更新回调函数"""
    print(f"配置文件 {config_name} 已更新!")
    # 这里可以添加处理配置更新的逻辑

# 注册配置更新回调
loader.register_update_callback(on_config_update)
```

### 完整示例

```python
from config_system import get_config_loader, shutdown_config_loader
import time

def on_config_update(config_name, config_content):
    """配置更新回调函数示例"""
    print(f"配置文件 {config_name} 已更新!")
    # 这里可以添加处理配置更新的逻辑

def main():
    # 获取配置加载器实例
    loader = get_config_loader()

    # 注册配置更新回调
    loader.register_update_callback(on_config_update)

    # 获取特定配置
    attributes_config = loader.get_config("basic/attributes")
    if attributes_config:
        print("成功加载属性配置")
        # 打印基础属性
        for attr_name, attr_info in attributes_config.get("primary_attributes", {}).items():
            print(f"{attr_name}: {attr_info.get('description', '无描述')}")

    # 获取配置中的特定值
    base_hit_rate = loader.get_value("systems/combat", "base_hit_rate", 0.9)
    print(f"基础命中率: {base_hit_rate}")

    # 演示热更新功能
    print("\n现在您可以修改配置文件中的内容，系统会自动检测并重新加载...")
    print("按 Ctrl+C 退出程序")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n正在关闭配置加载器...")
        shutdown_config_loader()
        print("程序已退出")

if __name__ == "__main__":
    main()
```

## 运行示例

首先确保您已经安装了所需的依赖包（参考上面的安装说明）。

您有两种方式运行示例：

**方式一：使用启动脚本（推荐）**

```bash
python run_config_example.py
```

这个脚本会自动检查并安装所需的依赖，然后运行示例。

**方式二：手动安装依赖后运行**

```bash
python -m config_system.example
```

**常见问题：**

1. 如果遇到 `ModuleNotFoundError: No module named 'watchdog'` 错误，请运行：
   ```bash
   pip install watchdog
   ```

2. 如果遇到 `ModuleNotFoundError: No module named 'yaml'` 错误，请运行：
   ```bash
   pip install PyYAML
   ```

运行示例后，您可以尝试修改任何配置文件，系统会自动检测到变化并重新加载，同时触发注册的回调函数。

## 配置文件格式

配置文件使用YAML格式，支持以下高级特性：

### 锚点和别名

```yaml
# 定义锚点
base_monster: &base_monster
  hp: 100
  mp: 50
  attack: 10

# 使用别名引用
goblin:
  <<: *base_monster  # 继承基础属性
  name: "哥布林"
  hp: 80  # 覆盖继承的hp值
```

### 多行文本

```yaml
description: |
  这是一段多行文本，
  可以包含换行符，
  适合用于长描述。

description: >
  这也是一段多行文本，
  但换行符会被转换为空格，
  适合用于段落文本。
```

### 复杂嵌套结构

```yaml
dungeon:
  name: "地下城"
  rooms:
    - id: "entrance"
      name: "入口"
      connections:
        - direction: "north"
          target: "corridor"
      monsters:
        - type: "goblin"
          count: [2, 4]
```

更多高级特性请参考 `configs/yaml_advanced_examples.yaml` 文件。

## API 参考

### ConfigLoader 类

#### 方法

- `get_config(config_name: str) -> Optional[Any]`
  获取指定配置文件内容

- `get_value(config_name: str, key_path: str, default: Any = None) -> Any`
  获取配置中的特定值，key_path使用点号分隔嵌套键

- `reload_config(config_name: str) -> bool`
  重新加载指定配置文件

- `register_update_callback(callback: Callable[[str, Any], None])`
  注册配置更新回调函数

- `unregister_update_callback(callback: Callable[[str, Any], None])`
  取消注册配置更新回调函数

- `load_all_configs() -> Dict[str, Any]`
  加载所有配置文件

- `shutdown()`
  关闭配置加载器，释放资源

### 全局函数

- `get_config_loader(config_dir: str = "configs") -> ConfigLoader`
  获取全局配置加载器实例

- `shutdown_config_loader()`
  关闭全局配置加载器

## 注意事项

1. 配置文件必须使用UTF-8编码
2. 配置文件扩展名必须是 `.yaml`
3. 配置热更新依赖于文件系统监视，在某些系统上可能有延迟
4. 多线程环境下，配置加载器是线程安全的
5. 修改配置文件后，确保YAML语法正确，否则可能导致加载失败

## 扩展

您可以根据需要扩展此配置系统，例如：

1. 添加配置验证功能，确保配置值符合预期
2. 实现配置版本控制，支持配置文件升级
3. 添加配置加密功能，保护敏感配置信息
4. 实现配置远程加载，支持从服务器获取配置
