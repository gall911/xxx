#!/usr/bin/env python3
"""
配置系统示例启动脚本

这个脚本会检查并安装必要的依赖，然后运行配置系统示例。
"""

import sys
import subprocess
import importlib

def check_and_install_package(package_name, import_name=None):
    """检查并安装Python包"""
    if import_name is None:
        import_name = package_name

    try:
        importlib.import_module(import_name)
        print(f"✓ {package_name} 已安装")
        return True
    except ImportError:
        print(f"✗ {package_name} 未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])
            print(f"✓ {package_name} 安装成功")
            return True
        except subprocess.CalledProcessError:
            print(f"✗ {package_name} 安装失败")
            return False

def main():
    """主函数"""
    print("MUD游戏配置系统示例")
    print("=" * 40)

    # 检查并安装依赖
    print("检查依赖...")
    deps_ok = True
    deps_ok &= check_and_install_package("PyYAML", "yaml")
    deps_ok &= check_and_install_package("watchdog")

    if not deps_ok:
        print("依赖安装失败，无法继续运行示例")
        sys.exit(1)

    print("
所有依赖已就绪，正在启动配置系统示例...
")

    # 运行示例
    try:
        from config_system.example import main as example_main
        example_main()
    except Exception as e:
        print(f"运行示例时出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
