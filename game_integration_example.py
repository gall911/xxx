#!/usr/bin/env python3
"""
游戏集成示例

这个示例展示了如何将配置系统集成到游戏主程序中，实现持续运行和热更新功能。
"""

import sys
import time
import threading
from config_system import get_config_loader, shutdown_config_loader

class Game:
    """游戏主类"""

    def __init__(self):
        # 初始化配置加载器
        self.config_loader = get_config_loader(
            enable_validation=True,
            enable_version_control=True
        )

        # 注册配置更新回调
        self.config_loader.register_update_callback(self.on_config_updated)

        # 游戏状态
        self.running = False
        self.game_thread = None

        # 加载初始配置
        self.load_game_configs()

    def load_game_configs(self):
        """加载游戏配置"""
        print("加载游戏配置...")

        # 加载战斗系统配置
        combat_config = self.config_loader.get_config("systems/combat")
        if combat_config:
            self.base_hit_rate = combat_config.get("base_hit_rate", 0.9)
            print(f"基础命中率: {self.base_hit_rate}")
        else:
            self.base_hit_rate = 0.9
            print("未找到战斗系统配置，使用默认基础命中率: 0.9")

        # 加载其他配置...
        print("游戏配置加载完成")

    def on_config_updated(self, config_name, config_content):
        """配置更新回调函数"""
        print(f"[热更新] 配置文件 {config_name} 已更新")

        # 根据配置名称处理不同的更新
        if config_name == "systems/combat":
            self.base_hit_rate = config_content.get("base_hit_rate", 0.9)
            print(f"[热更新] 基础命中率已更新为: {self.base_hit_rate}")

        # 可以添加更多配置处理逻辑...

    def game_loop(self):
        """游戏主循环"""
        print("游戏开始运行...")
        print("您可以修改配置文件，系统会自动检测并应用更改")
        print("按 Ctrl+C 停止游戏")

        try:
            while self.running:
                # 游戏逻辑处理
                self.process_game_logic()

                # 控制循环频率，避免CPU占用过高
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("收到停止信号，正在关闭游戏...")
        finally:
            self.running = False

    def process_game_logic(self):
        """处理游戏逻辑"""
        # 这里是您的游戏逻辑代码
        # 可以使用配置系统中的各种配置值

        # 示例：模拟战斗计算
        # hit_rate = self.base_hit_rate + player_bonus
        # if random.random() < hit_rate:
        #     print("攻击命中!")
        # else:
        #     print("攻击未命中!")
        pass

    def start(self):
        """启动游戏"""
        if self.running:
            print("游戏已在运行中")
            return

        self.running = True
        self.game_thread = threading.Thread(target=self.game_loop)
        self.game_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
        self.game_thread.start()

    def stop(self):
        """停止游戏"""
        if not self.running:
            print("游戏未在运行")
            return

        self.running = False
        if self.game_thread and self.game_thread.is_alive():
            self.game_thread.join(timeout=1.0)

        print("游戏已停止")

    def wait_for_shutdown(self):
        """等待游戏关闭"""
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
        finally:
            # 关闭配置加载器
            shutdown_config_loader()
            print("配置加载器已关闭，程序退出")

def main():
    """主函数"""
    print("=== MUD游戏配置系统集成示例 ===")

    # 创建并启动游戏
    game = Game()
    game.start()

    # 等待游戏关闭
    game.wait_for_shutdown()

if __name__ == "__main__":
    main()
    