#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_skill_loading():
    """测试技能加载功能"""
    print("测试技能加载功能...")
    
    try:
        # 导入技能加载器
        from typeclasses.spells.loader import load_spell_data, MAGIC_INDEX
        
        print(f"成功加载技能索引，共 {len(MAGIC_INDEX)} 个技能")
        print("技能索引内容:")
        for key, path in MAGIC_INDEX.items():
            print(f"  {key}: {path}")
        
        # 测试加载几个技能
        test_spells = ["fire.fireball", "ice.iceball", "fire.fb"]
        
        for spell_key in test_spells:
            print(f"\n测试加载技能: {spell_key}")
            try:
                spell_data = load_spell_data(spell_key)
                if spell_data:
                    print(f"  成功加载: {spell_data.get('name', '未知名称')}")
                    print(f"  描述: {spell_data.get('desc', '无描述')}")
                else:
                    print(f"  加载失败: 返回空数据")
            except Exception as e:
                print(f"  加载出错: {e}")
                
    except Exception as e:
        print(f"测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_skill_loading()