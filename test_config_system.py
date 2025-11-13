#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试配置系统脚本

这个脚本用于测试配置系统功能，包括保存版本、验证配置等。
"""

import os
import sys

# 添加项目路径到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.config_manager import game_config

def test_save_version():
    """测试保存版本功能"""
    print("测试保存版本功能...")

    # 获取属性配置
    try:
        attributes_config = game_config.get_config("basic/attributes")
        print(f"成功获取属性配置: {attributes_config['description']}")

        # 保存版本
        if game_config._instance._config_loader.enable_version_control and game_config._instance._config_loader.version_manager:
            version_id = game_config._instance._config_loader.version_manager.save_version(
                "basic/attributes", 
                attributes_config, 
                "测试保存的版本"
            )
            print(f"成功保存版本: {version_id}")
            return version_id
        else:
            print("版本控制功能未启用")
            return None
    except Exception as e:
        print(f"保存版本失败: {e}")
        return None

def test_list_versions():
    """测试列出版本功能"""
    print("\n测试列出版本功能...")

    try:
        versions = game_config.list_config_versions("basic/attributes")
        if versions:
            print(f"找到 {len(versions)} 个版本:")
            for version in versions:
                print(f"  版本 {version['version_id']}: {version['description']} ({version['datetime']})")
            return versions
        else:
            print("没有找到版本记录")
            return []
    except Exception as e:
        print(f"获取版本列表失败: {e}")
        return []

def test_validate_config():
    """测试验证配置功能"""
    print("\n测试验证配置功能...")

    try:
        errors = game_config.validate_config("basic/attributes")
        if not errors:
            print("配置验证通过")
            return True
        else:
            print("配置验证失败:")
            for error in errors:
                print(f"  - {error}")
            return False
    except Exception as e:
        print(f"验证配置失败: {e}")
        return False

def test_reload_config():
    """测试重新加载配置功能"""
    print("\n测试重新加载配置功能...")

    try:
        game_config.reload_config("basic/attributes")
        print("配置重新加载成功")
        return True
    except Exception as e:
        print(f"重新加载配置失败: {e}")
        return False

def main():
    """主测试函数"""
    print("开始测试配置系统...")

    # 测试保存版本
    version_id = test_save_version()

    # 测试列出版本
    versions = test_list_versions()

    # 测试验证配置
    test_validate_config()

    # 测试重新加载配置
    test_reload_config()

    print("\n测试完成!")
if __name__ == "__main__":
    main()
