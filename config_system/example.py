from .config_loader import get_config_loader, shutdown_config_loader
import time

def on_config_update(config_name, config_content):
    """配置更新回调函数示例"""
    print(f"配置文件 {config_name} 已更新!")
    # 这里可以添加处理配置更新的逻辑
    # 例如：重新加载游戏系统、通知相关模块等

def main():
    """主函数，演示配置加载器的使用"""
    # 获取配置加载器实例
    loader = get_config_loader()

    # 注册配置更新回调
    loader.register_update_callback(on_config_update)

    # 加载所有配置
    configs = loader.load_all_configs()
    print(f"已加载 {len(configs)} 个配置文件")

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
