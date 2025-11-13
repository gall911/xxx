
import time
import json
import yaml
import os
import random
import tracemalloc

def generate_test_data(size_kb):
    """生成指定大小的测试数据"""
    # 基础数据结构
    base_data = {
        "attribute_names": {
            "level": "等级",
            "exp": "经验",
            "exp_needed": "升级所需经验",
            "cultivation": "境界",
            "cultivation_level": "境界等级",
            "spirit_power": "灵力",
            "hp": "气血",
            "max_hp": "最大气血",
            "mana": "真元",
            "max_mana": "最大真元",
            "magic_power": "法力强度",
            "constitution": "根骨",
            "strength": "力量",
            "agility": "身法",
            "intelligence": "悟性",
            "fire_resistance": "火系抗性",
            "water_resistance": "水系抗性",
            "earth_resistance": "土系抗性",
            "air_resistance": "风系抗性",
            "lightning_resistance": "雷系抗性",
            "ice_resistance": "冰系抗性",
            "light_resistance": "光系抗性",
            "dark_resistance": "暗系抗性",
            "gold": "金币",
            "silver": "银币",
            "known_spells": "已知法术"
        }
    }

    # 计算需要多少个条目才能达到目标大小
    # 先保存一个基础数据，看它有多大
    with open('temp_size_test.json', 'w') as f:
        json.dump(base_data, f)

    base_size = os.path.getsize('temp_size_test.json') / 1024  # KB
    os.remove('temp_size_test.json')

    # 计算需要的条目数量
    items_needed = max(1, int(size_kb / base_size))

    # 生成数据
    test_data = {"data": []}
    for i in range(items_needed):
        # 为每个条目创建一个稍微不同的版本
        item = {}
        for key, value in base_data["attribute_names"].items():
            item[f"{key}_{i}"] = f"{value}_{i}"
        test_data["data"].append(item)

    return test_data

def test_config_performance(file_path, format_type):
    """测试配置文件加载性能"""
    # 开始内存跟踪
    tracemalloc.start()

    # 记录初始内存
    snapshot1 = tracemalloc.take_snapshot()

    # 记录开始时间
    start_time = time.time()

    # 加载配置
    if format_type == 'json':
        with open(file_path, 'r') as f:
            config = json.load(f)
    elif format_type == 'yaml':
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)

    # 记录结束时间
    end_time = time.time()

    # 记录加载后内存
    snapshot2 = tracemalloc.take_snapshot()

    # 计算内存差异
    top_stats = snapshot2.compare_to(snapshot1, 'lineno')
    mem_diff = sum(stat.size_diff for stat in top_stats) / 1024 / 1024  # MB

    # 输出结果
    file_size = os.path.getsize(file_path) / 1024  # KB
    print(f"文件: {file_path}")
    print(f"格式: {format_type}")
    print(f"文件大小: {file_size:.2f}KB")
    print(f"加载时间: {end_time - start_time:.4f}秒")
    print(f"内存增加: {mem_diff:.2f}MB")
    print(f"配置项数量: {len(config)}")
    print("-" * 40)

    # 停止内存跟踪
    tracemalloc.stop()

def run_tests():
    """运行不同大小的配置文件测试"""
    # 测试不同大小的文件
    test_sizes = [10, 50, 100, 500, 1000, 2000]  # KB

    for size in test_sizes:
        print(f"\n=== 测试 {size}KB 配置文件 ===")

        # 生成测试数据
        test_data = generate_test_data(size)

        # 保存为JSON格式
        json_file = f"test_{size}kb.json"
        with open(json_file, 'w') as f:
            json.dump(test_data, f)

        # 保存为YAML格式
        yaml_file = f"test_{size}kb.yaml"
        with open(yaml_file, 'w') as f:
            yaml.dump(test_data, f)

        # 测试JSON加载性能
        print("\n--- JSON格式 ---")
        test_config_performance(json_file, 'json')

        # 测试YAML加载性能
        print("\n--- YAML格式 ---")
        test_config_performance(yaml_file, 'yaml')

        # 清理测试文件
        os.remove(json_file)
        os.remove(yaml_file)

if __name__ == "__main__":
    run_tests()
