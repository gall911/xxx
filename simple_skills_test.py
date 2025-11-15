#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 设置Django环境变量
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')

def test_skills_display():
    """测试技能显示逻辑"""
    print("测试技能显示逻辑...")
    
    try:
        # 导入必要的模块
        from utils.json_cache import load_json
        import json
        
        # 设置魔法根目录
        MAGIC_ROOT = os.path.join(project_root, "world", "magic")
        INDEX_FILE = os.path.join(MAGIC_ROOT, "magic_index.json")
        
        # 加载索引文件
        with open(INDEX_FILE, "r", encoding="utf-8") as f:
            MAGIC_INDEX = json.load(f)
        
        print(f"成功加载技能索引，共 {len(MAGIC_INDEX)} 个技能")
        
        # 模拟玩家学会的技能
        player_skills = {
            'fire.fireball': {'level': 1},
            'ice.iceball': {'level': 1},
            'fire.fb': {'level': 1}
        }
        
        def load_spell_data(spell_key):
            """加载法术数据"""
            if spell_key not in MAGIC_INDEX:
                return None
            
            # 获取文件路径
            file_path = MAGIC_INDEX[spell_key]
            
            # 如果不是绝对路径，则相对于MAGIC_ROOT
            if not os.path.isabs(file_path):
                file_path = os.path.join(MAGIC_ROOT, file_path)
            
            # YAML文件需要特殊处理
            if file_path.endswith(".yaml"):
                import yaml
                with open(file_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            else:
                return load_json(file_path)
        
        print("\n模拟技能显示:")
        print("你已学会的技能：")
        
        # 遍历玩家技能
        for skill_key, skill_data in player_skills.items():
            level = skill_data.get("level", 1)
            try:
                # 直接加载法术数据（现在每个文件都包含完整的法术定义）
                spell_data = load_spell_data(skill_key)
                
                if spell_data and 'name' in spell_data:
                    # 只显示技能键名的最后一部分（例如 fire.fb 显示为 fb）
                    display_key = skill_key.split(".")[-1] if "." in skill_key else skill_key
                    desc = spell_data.get('desc', '无描述')
                    print(f"- {spell_data['name']} (|m{display_key}|n) (等级 {level}): {desc}")
                else:
                    # 只显示技能键名的最后一部分（例如 fire.fb 显示为 fb）
                    display_key = skill_key.split(".")[-1] if "." in skill_key else skill_key
                    print(f"- |m{display_key}|n (等级 {level})")
            except Exception as e:
                # 如果加载法术数据失败，显示基本技能信息
                display_key = skill_key.split(".")[-1] if "." in skill_key else skill_key
                print(f"- |m{display_key}|n (等级 {level})")
        
        print("\n测试完成!")
        
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_skills_display()