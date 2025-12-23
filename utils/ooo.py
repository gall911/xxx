"""
benchmark_test.py
用于测试 YAML vs JSON 的读取速度
"""
import time
import yaml
import json
import os

# 构造一个比较大的测试数据
test_data = {
    f"item_{i}": {
        "name": f"测试物品_{i}",
        "desc": "这是一个用于测试性能的物品描述，越长越好。",
        "stats": {"str": 10, "agi": 5, "int": 20},
        "tags": ["test", "benchmark", "equipment"]
    } for i in range(5000) # 生成 5000 个物品
}

# 写入文件用于测试
with open("test.yaml", "w", encoding="utf-8") as f:
    yaml.dump(test_data, f, allow_unicode=True)

with open("test.json", "w", encoding="utf-8") as f:
    json.dump(test_data, f, ensure_ascii=False, indent=2)

print(f"=== 测试数据生成完毕 (5000个物品) ===")
print(f"YAML 文件大小: {os.path.getsize('test.yaml') / 1024:.2f} KB")
print(f"JSON 文件大小: {os.path.getsize('test.json') / 1024:.2f} KB")
print("-" * 30)

# --- 测试 YAML ---
start = time.perf_counter()
with open("test.yaml", "r", encoding="utf-8") as f:
    # 注意：默认的 Loader 很慢，稍后会提到加速
    data = yaml.safe_load(f)
end = time.perf_counter()
print(f"YAML 读取耗时: {end - start:.4f} 秒")

# --- 测试 YAML (C语言加速版) ---
try:
    from yaml import CLoader as Loader
    start = time.perf_counter()
    with open("test.yaml", "r", encoding="utf-8") as f:
        data = yaml.load(f, Loader=Loader)
    end = time.perf_counter()
    print(f"YAML (CLoader) 读取耗时: {end - start:.4f} 秒")
except ImportError:
    print("未安装 LibYAML，无法测试 CLoader 加速版")

# --- 测试 JSON ---
start = time.perf_counter()
with open("test.json", "r", encoding="utf-8") as f:
    data = json.load(f)
end = time.perf_counter()
print(f"JSON 读取耗时: {end - start:.4f} 秒")

# --- 清理文件 ---
# os.remove("test.yaml")
# os.remove("test.json")