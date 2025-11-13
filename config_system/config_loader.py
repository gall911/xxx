import os
import time
import threading
import yaml
from typing import Dict, Any, Optional, Callable, Set, List
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .validator import get_config_validator, ConfigValidator
from .version_manager import get_config_version_manager, ConfigVersionManager

class ConfigFile:
    """配置文件类，跟踪文件内容和修改时间"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = None
        self.last_modified = 0
        self.load()

    def load(self) -> bool:
        """加载文件内容，返回是否成功"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = yaml.safe_load(f)
                self.last_modified = os.path.getmtime(self.file_path)
                return True
        except Exception as e:
            print(f"加载配置文件 {self.file_path} 失败: {e}")
            return False

    def is_modified(self) -> bool:
        """检查文件是否已修改"""
        try:
            current_modified = os.path.getmtime(self.file_path)
            return current_modified > self.last_modified
        except OSError:
            return False

    def reload(self) -> bool:
        """重新加载文件内容，返回是否成功"""
        return self.load()

class ConfigCache:
    """配置缓存类，管理所有配置文件的缓存"""

    def __init__(self):
        self._cache: Dict[str, ConfigFile] = {}
        self._lock = threading.RLock()

    def get(self, config_path: str) -> Optional[Any]:
        """获取配置内容"""
        with self._lock:
            if config_path not in self._cache:
                return None
            return self._cache[config_path].content

    def load(self, config_path: str) -> bool:
        """加载配置文件到缓存"""
        with self._lock:
            if not os.path.exists(config_path):
                return False

            config_file = ConfigFile(config_path)
            if config_file.content is not None:
                self._cache[config_path] = config_file
                return True
            return False

    def reload(self, config_path: str) -> bool:
        """重新加载配置文件"""
        with self._lock:
            if config_path not in self._cache:
                return self.load(config_path)

            return self._cache[config_path].reload()

    def check_modified(self) -> Set[str]:
        """检查所有缓存文件是否有修改，返回已修改的文件路径集合"""
        with self._lock:
            modified_files = set()
            for path, config_file in self._cache.items():
                if config_file.is_modified():
                    modified_files.add(path)
            return modified_files

    def remove(self, config_path: str) -> bool:
        """从缓存中移除配置文件"""
        with self._lock:
            if config_path in self._cache:
                del self._cache[config_path]
                return True
            return False

    def clear(self):
        """清空缓存"""
        with self._lock:
            self._cache.clear()

class ConfigFileWatcher(FileSystemEventHandler):
    """配置文件监视器，监视文件变化并触发回调"""

    def __init__(self, callback: Callable[[str], None]):
        self.callback = callback
        self.observer = Observer()

    def start(self, watch_dir: str):
        """开始监视目录"""
        self.observer.schedule(self, watch_dir, recursive=True)
        self.observer.start()

    def stop(self):
        """停止监视"""
        self.observer.stop()
        self.observer.join()

    def on_modified(self, event):
        """文件修改事件处理"""
        if not event.is_directory and event.src_path.endswith('.yaml'):
            self.callback(event.src_path)

class ConfigLoader:
    """配置加载器，提供配置加载、缓存和热更新功能"""

    def __init__(self, config_dir: str = "configs", 
                 enable_validation: bool = True, 
                 enable_version_control: bool = True,
                 versions_dir: str = "config_versions"):
        self.config_dir = config_dir
        self.cache = ConfigCache()
        self.watcher = ConfigFileWatcher(self._on_file_changed)
        self._update_callbacks: Set[Callable[[str, Any], None]] = set()
        self._lock = threading.RLock()
        
        # 验证和版本控制
        self.enable_validation = enable_validation
        self.enable_version_control = enable_version_control
        self.validator = get_config_validator() if enable_validation else None
        self.version_manager = get_config_version_manager(versions_dir) if enable_version_control else None

        # 加载所有配置文件
        self.load_all_configs()

        # 启动文件监视器
        self.watcher.start(self.config_dir)

    def load_all_configs(self) -> Dict[str, Any]:
        """加载所有配置文件"""
        configs = {}
        for root, _, files in os.walk(self.config_dir):
            for file in files:
                if file.endswith('.yaml'):
                    file_path = os.path.join(root, file)
                    if self.cache.load(file_path):
                        # 获取相对于config_dir的路径作为配置名
                        rel_path = os.path.relpath(file_path, self.config_dir)
                        config_name = os.path.splitext(rel_path)[0].replace(os.sep, '/')
                        config_data = self.cache.get(file_path)
                        
                        # 验证配置
                        if self.enable_validation and self.validator:
                            errors = self.validator.validate_config(config_name, config_data)
                            if errors:
                                print(f"配置 {config_name} 验证失败:")
                                for error in errors:
                                    print(f"  - {error}")
                                continue  # 跳过验证失败的配置
                        
                        # 保存版本（仅在内容发生变化时）
                        if self.enable_version_control and self.version_manager:
                            # 检查是否已经有相同内容的版本
                            if not self._has_identical_version(config_name, config_data):
                                self.version_manager.save_version(
                                    config_name, config_data, 
                                    f"初始加载于 {time.strftime('%Y-%m-%d %H:%M:%S')}"
                                )
                        
                        configs[config_name] = config_data
        return configs

    def _has_identical_version(self, config_name: str, new_data: Any) -> bool:
        """检查是否已经有相同内容的版本"""
        if not self.enable_version_control or not self.version_manager:
            return False
            
        # 获取最近的版本
        versions = self.version_manager.list_versions(config_name)
        if not versions:
            return False
            
        # 检查最新的版本是否与当前内容相同
        latest_version = versions[0]
        return self._compare_data(latest_version.data, new_data)

    def _compare_data(self, data1: Any, data2: Any) -> bool:
        """比较两个数据结构是否相同"""
        if type(data1) != type(data2):
            return False
            
        if isinstance(data1, dict):
            if set(data1.keys()) != set(data2.keys()):
                return False
            for key in data1:
                if not self._compare_data(data1[key], data2[key]):
                    return False
            return True
            
        elif isinstance(data1, list):
            if len(data1) != len(data2):
                return False
            for i in range(len(data1)):
                if not self._compare_data(data1[i], data2[i]):
                    return False
            return True
            
        else:
            return data1 == data2

    def get_config(self, config_name: str) -> Optional[Any]:
        """获取指定配置"""
        # 将配置名转换为文件路径
        file_path = os.path.join(self.config_dir, f"{config_name}.yaml")
        return self.cache.get(file_path)

    def get_value(self, config_name: str, key_path: str, default: Any = None) -> Any:
        """
        获取配置中的特定值

        参数:
            config_name: 配置名称
            key_path: 键路径，用点号分隔，如 "combat_system.base_hit_rate"
            default: 默认值，如果找不到则返回此值

        返回:
            配置值或默认值
        """
        config = self.get_config(config_name)
        if not config:
            return default

        keys = key_path.split('.')
        value = config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def reload_config(self, config_name: str) -> bool:
        """
        重新加载指定配置

        参数:
            config_name: 要重新加载的配置名

        返回:
            是否成功重新加载
        """
        file_path = os.path.join(self.config_dir, f"{config_name}.yaml")
        if not os.path.exists(file_path):
            return False

        success = self.cache.reload(file_path)
        if success:
            config_content = self.cache.get(file_path)
            
            # 验证配置
            if self.enable_validation and self.validator:
                errors = self.validator.validate_config(config_name, config_content)
                if errors:
                    print(f"配置 {config_name} 验证失败:")
                    for error in errors:
                        print(f"  - {error}")
                    return False  # 验证失败，不应用新配置
            
            # 保存版本（仅在内容发生变化时）
            if self.enable_version_control and self.version_manager:
                # 检查是否已经有相同内容的版本
                if not self._has_identical_version(config_name, config_content):
                    self.version_manager.save_version(
                        config_name, config_content, 
                        f"重新加载于 {time.strftime('%Y-%m-%d %H:%M:%S')}"
                    )
            
            # 通知所有注册的回调函数
            with self._lock:
                for callback in self._update_callbacks:
                    callback(config_name, config_content)

        return success

    def register_update_callback(self, callback: Callable[[str, Any], None]):
        """
        注册配置更新回调函数

        参数:
            callback: 回调函数，接收配置名和配置内容作为参数
        """
        with self._lock:
            self._update_callbacks.add(callback)

    def unregister_update_callback(self, callback: Callable[[str, Any], None]):
        """
        取消注册配置更新回调函数

        参数:
            callback: 要取消注册的回调函数
        """
        with self._lock:
            self._update_callbacks.discard(callback)

    def _on_file_changed(self, file_path: str):
        """文件变化处理"""
        if not file_path.endswith('.yaml'):
            return

        # 获取相对于config_dir的路径作为配置名
        try:
            rel_path = os.path.relpath(file_path, self.config_dir)
            config_name = os.path.splitext(rel_path)[0].replace(os.sep, '/')

            # 重新加载配置
            if self.cache.reload(file_path):
                # 通知所有注册的回调函数
                with self._lock:
                    config_content = self.cache.get(file_path)
                    for callback in self._update_callbacks:
                        callback(config_name, config_content)
        except Exception as e:
            print(f"处理配置文件更新失败 {file_path}: {e}")

    def shutdown(self):
        """关闭配置加载器"""
        self.watcher.stop()
        self.cache.clear()
    
    # 配置验证相关方法
    def validate_config(self, config_name: str) -> List[str]:
        """
        验证指定配置
        
        参数:
            config_name: 配置名
            
        返回:
            错误消息列表，空列表表示验证通过
        """
        if not self.enable_validation or not self.validator:
            return []  # 未启用验证功能
            
        config_data = self.get_config(config_name)
        if not config_data:
            return [f"配置 {config_name} 不存在"]
            
        return self.validator.validate_config(config_name, config_data)
    
    def add_validation_rule(self, config_name: str, key_path: str, rule_type: str, **kwargs):
        """
        添加验证规则
        
        参数:
            config_name: 配置名
            key_path: 键路径，用点号分隔
            rule_type: 规则类型，可选值: type, range, length, regex, enum
            **kwargs: 规则参数
        """
        if not self.enable_validation or not self.validator:
            print("验证功能未启用")
            return
            
        if rule_type == "type":
            self.validator.add_type_rule(config_name, key_path, **kwargs)
        elif rule_type == "range":
            self.validator.add_range_rule(config_name, key_path, **kwargs)
        elif rule_type == "length":
            self.validator.add_length_rule(config_name, key_path, **kwargs)
        elif rule_type == "regex":
            self.validator.add_regex_rule(config_name, key_path, **kwargs)
        elif rule_type == "enum":
            self.validator.add_enum_rule(config_name, key_path, **kwargs)
        else:
            print(f"未知的验证规则类型: {rule_type}")
    
    # 版本控制相关方法
    def list_config_versions(self, config_name: str) -> List[Dict[str, Any]]:
        """
        列出指定配置的所有版本
        
        参数:
            config_name: 配置名
            
        返回:
            版本信息列表
        """
        if not self.enable_version_control or not self.version_manager:
            return []  # 未启用版本控制
            
        versions = self.version_manager.list_versions(config_name)
        return [
            {
                "version_id": v.version_id,
                "timestamp": v.timestamp,
                "datetime": v.datetime.isoformat(),
                "description": v.description
            }
            for v in versions
        ]
    
    def restore_config_version(self, config_name: str, version_id: str, save_current: bool = True) -> bool:
        """
        恢复到指定版本的配置
        
        参数:
            config_name: 配置名
            version_id: 版本ID
            save_current: 是否保存当前配置为新版本
            
        返回:
            是否成功恢复
        """
        if not self.enable_version_control or not self.version_manager:
            print("版本控制功能未启用")
            return False
            
        # 保存当前配置
        if save_current:
            current_config = self.get_config(config_name)
            if current_config:
                self.version_manager.save_version(
                    config_name, current_config, 
                    f"恢复前保存于 {time.strftime('%Y-%m-%d %H:%M:%S')}"
                )
        
        # 恢复指定版本
        restored_config = self.version_manager.restore_version(config_name, version_id)
        if not restored_config:
            print(f"无法恢复版本 {version_id}")
            return False
            
        # 写入文件
        file_path = os.path.join(self.config_dir, f"{config_name}.yaml")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                yaml.dump(restored_config, f, default_flow_style=False, allow_unicode=True)
            
            # 重新加载配置
            return self.reload_config(config_name)
        except Exception as e:
            print(f"写入配置文件失败: {e}")
            return False
    
    def compare_config_versions(self, config_name: str, version_id1: str, version_id2: str) -> Dict[str, Any]:
        """
        比较两个版本的配置
        
        参数:
            config_name: 配置名
            version_id1: 第一个版本ID
            version_id2: 第二个版本ID
            
        返回:
            比较结果
        """
        if not self.enable_version_control or not self.version_manager:
            return {"error": "版本控制功能未启用"}
            
        return self.version_manager.compare_versions(config_name, version_id1, version_id2)

# 全局配置加载器实例
_config_loader: Optional[ConfigLoader] = None

def get_config_loader(config_dir: str = "configs", 
                    enable_validation: bool = True, 
                    enable_version_control: bool = True,
                    versions_dir: str = "config_versions") -> ConfigLoader:
    """
    获取全局配置加载器实例

    参数:
        config_dir: 配置目录路径
        enable_validation: 是否启用配置验证
        enable_version_control: 是否启用版本控制
        versions_dir: 版本存储目录

    返回:
        配置加载器实例
    """
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader(
            config_dir=config_dir,
            enable_validation=enable_validation,
            enable_version_control=enable_version_control,
            versions_dir=versions_dir
        )
    return _config_loader

def shutdown_config_loader():
    """关闭全局配置加载器"""
    global _config_loader
    if _config_loader is not None:
        _config_loader.shutdown()
        _config_loader = None