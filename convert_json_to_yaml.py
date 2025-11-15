#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
将JSON格式的技能文件转换为YAML格式
"""

import os
import json
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    print("错误: 未安装PyYAML库，请运行 'pip install PyYAML' 安装")
    YAML_AVAILABLE = False
    exit(1)

def convert_json_to_yaml(json_file_path, yaml_file_path):
    """
    将单个JSON文件转换为YAML文件
    """
    try:
        # 读取JSON文件
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 写入YAML文件
        with open(yaml_file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False, indent=2)
        
        print(f"已转换: {json_file_path} -> {yaml_file_path}")
        return True
    except Exception as e:
        print(f"转换失败 {json_file_path}: {e}")
        return False

def convert_all_spells():
    """
    转换所有技能文件
    """
    project_root = os.path.dirname(os.path.abspath(__file__))
    magic_root = os.path.join(project_root, "world", "magic")
    
    # 遍历magic目录下的所有JSON文件
    for root, dirs, files in os.walk(magic_root):
        for file in files:
            if file.endswith('.json'):
                json_file_path = os.path.join(root, file)
                # 生成对应的YAML文件名
                yaml_file_path = os.path.join(root, file[:-5] + '.yaml')  # 替换.json为.yaml
                
                # 转换文件
                convert_json_to_yaml(json_file_path, yaml_file_path)
    
    # 更新索引文件
    update_index_file()

def update_index_file():
    """
    更新索引文件，将.json替换为.yaml
    """
    project_root = os.path.dirname(os.path.abspath(__file__))
    index_file_path = os.path.join(project_root, "world", "magic", "magic_index.json")
    
    try:
        # 读取索引文件
        with open(index_file_path, 'r', encoding='utf-8') as f:
            index_data = json.load(f)
        
        # 更新文件路径
        updated = False
        for key, file_path in index_data.items():
            if file_path.endswith('.json'):
                index_data[key] = file_path[:-5] + '.yaml'  # 替换.json为.yaml
                updated = True
        
        # 如果有更新，写回文件
        if updated:
            with open(index_file_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, ensure_ascii=False, indent=4)
            print("已更新索引文件，将所有技能指向YAML文件")
        else:
            print("索引文件无需更新")
            
    except Exception as e:
        print(f"更新索引文件失败: {e}")

if __name__ == "__main__":
    print("开始转换JSON技能文件为YAML格式...")
    convert_all_spells()
    print("转换完成!")