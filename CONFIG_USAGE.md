# 配置系统使用指南

## 概述

本配置系统提供了完整的配置文件加载、缓存、验证、版本控制和热更新功能，适用于MUD游戏或其他需要动态配置的应用程序。

## 基本用法

### 1. 作为库集成到游戏中

```python
from config_system import get_config_loader

# 获取配置加载器实例
loader = get_config_loader()

# 获取配置
config = loader.get_config("systems/combat")

# 获取配置中的特定值
hit_rate = loader.get_value("systems/combat", "base_hit_rate", 0.9)
```

### 2. 作为独立服务运行

可以使用守护进程模式运行配置系统，使其作为后台服务持续监视配置文件变化：

```bash
# 启动配置守护进程
python config_daemon.py start

# 检查状态
python config_daemon.py status

# 停止守护进程
python config_daemon.py stop

# 重启守护进程
python config_daemon.py restart

# 前台运行（主要用于调试）
python config_daemon.py run
```

## 配置验证功能

### 添加验证规则

```python
# 添加类型验证
loader.add_validation_rule("systems/combat", "base_hit_rate", "type", expected_type="float")

# 添加范围验证
loader.add_validation_rule("systems/combat", "base_hit_rate", "range", min_val=0.0, max_val=1.0)

# 添加长度验证
loader.add_validation_rule("npcs/merchants", "name", "length", min_len=1, max_len=50)

# 添加正则表达式验证
loader.add_validation_rule("basic/realms", "realm_id", "regex", pattern=r"^[a-z_]+$")

# 添加枚举值验证
loader.add_validation_rule("items/weapons", "weapon_type", "enum", valid_values=["sword", "axe", "bow"])
```

### 验证配置

```python
# 验证特定配置
errors = loader.validate_config("systems/combat")
if errors:
    for error in errors:
        print(f"验证错误: {error}")
```

## 版本控制功能

### 列出版本

```python
# 列出配置的所有版本
versions = loader.list_config_versions("systems/combat")
for version in versions:
    print(f"版本 {version['version_id']}: {version['description']} ({version['datetime']})")
```

### 恢复版本

```python
# 恢复到指定版本
if versions:
    loader.restore_config_version("systems/combat", versions[0]["version_id"])
```

### 比较版本

```python
# 比较两个版本
if len(versions) >= 2:
    diff = loader.compare_config_versions("systems/combat", versions[0]["version_id"], versions[1]["version_id"])
    print("版本差异:")
    for change in diff["differences"]:
        print(f"  {change['path']}: {change['type']}")
```

## 完整示例

参考以下文件以获取更完整的使用示例：

- `game_integration_example.py` - 展示如何将配置系统集成到游戏主程序中
- `config_system/example.py` - 基本使用示例
- `config_daemon.py` - 守护进程实现

## 注意事项

1. 配置文件必须使用UTF-8编码
2. 配置文件扩展名必须是 `.yaml`
3. 启用版本控制会创建 `config_versions` 目录存储版本历史
4. 验证失败时，配置不会被加载
5. 守护进程模式下，配置更新会自动应用，无需重启游戏

## 高级用法

### 自定义验证规则

```python
from config_system import ValidationRule

class CustomRule(ValidationRule):
    def validate(self, value):
        # 自定义验证逻辑
        return True

    def get_error_message(self, key, value):
        return f"自定义验证失败: {key} = {value}"

# 添加自定义规则
loader.validator.add_rule("config_name", "key_path", CustomRule())
```

### 配置加密

配置系统未来将支持配置加密功能，可以保护敏感配置信息。

### 远程配置

配置系统未来将支持从远程服务器加载配置，便于分布式系统管理。
