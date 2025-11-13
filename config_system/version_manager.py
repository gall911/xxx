"""
配置版本控制模块

提供配置文件的版本管理功能，包括保存、恢复和比较配置版本。
"""

import os
import json
import time
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

class ConfigVersion:
    """配置版本类"""

    def __init__(self, config_name: str, version_id: str, timestamp: float, 
                 description: str = "", data: Optional[Dict[str, Any]] = None):
        self.config_name = config_name
        self.version_id = version_id
        self.timestamp = timestamp
        self.description = description
        self.data = data

    @property
    def datetime(self) -> datetime:
        """获取时间戳对应的datetime对象"""
        return datetime.fromtimestamp(self.timestamp)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "config_name": self.config_name,
            "version_id": self.version_id,
            "timestamp": self.timestamp,
            "description": self.description,
            "data": self.data
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConfigVersion':
        """从字典创建配置版本对象"""
        return cls(
            config_name=data["config_name"],
            version_id=data["version_id"],
            timestamp=data["timestamp"],
            description=data.get("description", ""),
            data=data.get("data")
        )

class ConfigVersionManager:
    """配置版本管理器"""

    def __init__(self, versions_dir: str = "config_versions"):
        self.versions_dir = versions_dir
        os.makedirs(versions_dir, exist_ok=True)

    def _get_version_file_path(self, config_name: str, version_id: str) -> str:
        """获取版本文件路径"""
        return os.path.join(self.versions_dir, f"{config_name}_{version_id}.json")

    def _generate_version_id(self) -> str:
        """生成版本ID"""
        return str(int(time.time() * 1000))  # 使用毫秒时间戳作为版本ID

    def save_version(self, config_name: str, config_data: Dict[str, Any], 
                    description: str = "") -> ConfigVersion:
        """保存配置版本"""
        version_id = self._generate_version_id()
        version = ConfigVersion(
            config_name=config_name,
            version_id=version_id,
            timestamp=time.time(),
            description=description,
            data=config_data
        )

        version_file = self._get_version_file_path(config_name, version_id)
        with open(version_file, 'w', encoding='utf-8') as f:
            json.dump(version.to_dict(), f, ensure_ascii=False, indent=2)

        return version

    def load_version(self, config_name: str, version_id: str) -> Optional[ConfigVersion]:
        """加载配置版本"""
        version_file = self._get_version_file_path(config_name, version_id)
        if not os.path.exists(version_file):
            return None

        try:
            with open(version_file, 'r', encoding='utf-8') as f:
                version_data = json.load(f)
                return ConfigVersion.from_dict(version_data)
        except (json.JSONDecodeError, KeyError):
            return None

    def list_versions(self, config_name: str) -> List[ConfigVersion]:
        """列出配置的所有版本"""
        versions = []
        prefix = f"{config_name}_"

        for file in os.listdir(self.versions_dir):
            if file.startswith(prefix) and file.endswith(".json"):
                version_id = file[len(prefix):-5]  # 提取版本ID
                version = self.load_version(config_name, version_id)
                if version:
                    versions.append(version)

        # 按时间戳降序排序
        versions.sort(key=lambda v: v.timestamp, reverse=True)
        return versions

    def delete_version(self, config_name: str, version_id: str) -> bool:
        """删除配置版本"""
        version_file = self._get_version_file_path(config_name, version_id)
        if os.path.exists(version_file):
            os.remove(version_file)
            return True
        return False

    def restore_version(self, config_name: str, version_id: str) -> Optional[Dict[str, Any]]:
        """恢复到指定版本的配置"""
        version = self.load_version(config_name, version_id)
        if version:
            return version.data
        return None

    def compare_versions(self, config_name: str, version_id1: str, version_id2: str) -> Dict[str, Any]:
        """比较两个版本的配置"""
        version1 = self.load_version(config_name, version_id1)
        version2 = self.load_version(config_name, version_id2)

        if not version1 or not version2:
            return {"error": "版本不存在"}

        # 简单比较，实际应用中可能需要更复杂的差异算法
        data1 = version1.data
        data2 = version2.data

        # 找出差异
        differences = self._find_differences(data1, data2)

        return {
            "version1": {
                "id": version1.version_id,
                "timestamp": version1.timestamp,
                "datetime": version1.datetime.isoformat(),
                "description": version1.description
            },
            "version2": {
                "id": version2.version_id,
                "timestamp": version2.timestamp,
                "datetime": version2.datetime.isoformat(),
                "description": version2.description
            },
            "differences": differences
        }

    def _find_differences(self, data1: Any, data2: Any, path: str = "") -> List[Dict[str, Any]]:
        """找出两个数据结构之间的差异"""
        differences = []

        # 处理字典类型
        if isinstance(data1, dict) and isinstance(data2, dict):
            # 找出所有键
            all_keys = set(data1.keys()) | set(data2.keys())

            for key in all_keys:
                current_path = f"{path}.{key}" if path else key

                if key not in data1:
                    differences.append({
                        "path": current_path,
                        "type": "added",
                        "value": data2[key]
                    })
                elif key not in data2:
                    differences.append({
                        "path": current_path,
                        "type": "removed",
                        "value": data1[key]
                    })
                else:
                    # 递归比较值
                    nested_diffs = self._find_differences(
                        data1[key], data2[key], current_path
                    )
                    differences.extend(nested_diffs)

        # 处理列表类型
        elif isinstance(data1, list) and isinstance(data2, list):
            # 简单比较，实际应用中可能需要更复杂的列表比较算法
            if len(data1) != len(data2) or data1 != data2:
                differences.append({
                    "path": path,
                    "type": "changed",
                    "old_value": data1,
                    "new_value": data2
                })

        # 处理其他类型
        elif data1 != data2:
            differences.append({
                "path": path,
                "type": "changed",
                "old_value": data1,
                "new_value": data2
            })

        return differences

    def cleanup_old_versions(self, config_name: str, keep_count: int = 10) -> int:
        """清理旧版本，只保留最新的指定数量版本"""
        versions = self.list_versions(config_name)

        if len(versions) <= keep_count:
            return 0

        # 删除多余的旧版本
        deleted_count = 0
        for version in versions[keep_count:]:
            if self.delete_version(config_name, version.version_id):
                deleted_count += 1

        return deleted_count

    def export_version(self, config_name: str, version_id: str, export_path: str) -> bool:
        """导出版本到指定路径"""
        version = self.load_version(config_name, version_id)
        if not version:
            return False

        try:
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(version.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except (IOError, json.JSONDecodeError):
            return False

    def import_version(self, import_path: str) -> Optional[ConfigVersion]:
        """从指定路径导入版本"""
        if not os.path.exists(import_path):
            return None

        try:
            with open(import_path, 'r', encoding='utf-8') as f:
                version_data = json.load(f)
                version = ConfigVersion.from_dict(version_data)

                # 保存到版本目录
                version_file = self._get_version_file_path(
                    version.config_name, version.version_id
                )
                shutil.copy2(import_path, version_file)

                return version
        except (IOError, json.JSONDecodeError, KeyError):
            return None

# 全局配置版本管理器实例
_config_version_manager: Optional[ConfigVersionManager] = None

def get_config_version_manager(versions_dir: str = "config_versions") -> ConfigVersionManager:
    """获取全局配置版本管理器实例"""
    global _config_version_manager
    if _config_version_manager is None:
        _config_version_manager = ConfigVersionManager(versions_dir)
    return _config_version_manager
