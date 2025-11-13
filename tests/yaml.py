import time
import json
import yaml
import psutil
import os

def test_config_performance(file_path, format_type):
    # 获取当前进程
    process = psutil.Process(os.getpid())
    
    # 记录初始内存
    mem_before = process.memory_info().rss / 1024 / 1024  # MB
    
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
    mem_after = process.memory_info().rss / 1024 / 1024  # MB
    
    # 输出结果
    print(f"文件: {file_path}")
    print(f"格式: {format_type}")
    print(f"加载时间: {end_time - start_time:.4f}秒")
    print(f"内存增加: {mem_after - mem_before:.2f}MB")
    print(f"配置项数量: {len(config)}")
    print("-" * 40)
