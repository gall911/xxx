#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试脚本用于验证xx.py命令中attributes获取功能的修复
"""

class MockAttribute:
    """模拟Evennia的Attribute对象"""
    def __init__(self, key, value):
        self.key = key
        self.value = value

class MockAttributesManager:
    """模拟Evennia的Attributes管理器"""
    def __init__(self):
        self._attrs = {}
    
    def add(self, key, value):
        """添加属性"""
        self._attrs[key] = MockAttribute(key, value)
    
    def all(self):
        """返回所有属性"""
        return list(self._attrs.values())
    
    def get_all_cached(self):
        """模拟get_all_cached方法"""
        return {attr.key: attr.value for attr in self._attrs.values()}
    
    def __getattr__(self, name):
        """支持通过属性名直接访问"""
        if name in self._attrs:
            return self._attrs[name].value
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

class MockObject:
    """模拟Evennia对象"""
    def __init__(self, key):
        self.key = key
        self.attributes = MockAttributesManager()
        
        # 添加一些测试属性
        self.attributes.add("hp", 100)
        self.attributes.add("mp", 50)
        self.attributes.add("level", 10)
        self.attributes.add("exp", 1000)
        self.attributes.add("nick", "test_player")
        self.attributes.add("title", "冒险者")
        self.attributes.add("class", "战士")

def format_value(value):
    """简化版的格式化函数"""
    if value is None:
        return "None"
    if isinstance(value, bool):
        return "True" if value else "False"
    if isinstance(value, str):
        return f"'{value}'"
    return str(value)

def list_attributes_only(target):
    """
    改进后的list_attributes_only函数
    """
    print(f"【{target.key}的Attributes】")
    
    # 获取Attributes
    attrs = {}
    if hasattr(target, "attributes") and target.attributes:
        try:
            # 尝试多种方法获取Attributes
            
            # 方法1: 使用.all()方法获取所有属性（如果可用）
            try:
                all_attrs = target.attributes.all()
                if all_attrs:
                    # 检查all_attrs是否是可迭代对象
                    if hasattr(all_attrs, '__iter__') and not isinstance(all_attrs, (str, bytes)):
                        for attr in all_attrs:
                            try:
                                # Evennia的Attribute对象通常有key和value属性
                                if hasattr(attr, 'key') and hasattr(attr, 'value'):
                                    attrs[attr.key] = attr.value
                                else:
                                    # 如果不是Attribute对象，直接使用
                                    attrs[str(attr)] = attr
                            except:
                                pass
                    else:
                        # 如果all_attrs不是可迭代对象，尝试将其作为单个属性处理
                        try:
                            if hasattr(all_attrs, 'key') and hasattr(all_attrs, 'value'):
                                attrs[all_attrs.key] = all_attrs.value
                        except:
                            pass
            except Exception as e:
                pass  # 继续尝试其他方法
            
            # 方法2: 如果方法1没有获取到属性，尝试使用.get_all_cached()（如果存在）
            if not attrs:
                try:
                    if hasattr(target.attributes, 'get_all_cached'):
                        cached_attrs = target.attributes.get_all_cached()
                        if cached_attrs and hasattr(cached_attrs, 'items'):
                            for key, value in cached_attrs.items():
                                attrs[key] = value
                except:
                    pass
            
            # 方法3: 如果还没有获取到属性，尝试使用.__dict__访问
            if not attrs:
                try:
                    if hasattr(target.attributes, '__dict__'):
                        attr_dict = getattr(target.attributes, '__dict__', {})
                        # 过滤掉私有属性和方法
                        for key, value in attr_dict.items():
                            if not key.startswith('_') and not callable(value):
                                attrs[key] = value
                except:
                    pass
            
            # 方法4: 如果仍然没有获取到属性，尝试遍历dir()
            if not attrs:
                try:
                    # 遍历所有可能的属性
                    for key in dir(target.attributes):
                        if not key.startswith('_') and not callable(getattr(target.attributes, key, None)):
                            try:
                                value = getattr(target.attributes, key, None)
                                # 排除一些特殊的属性
                                if value is not None and not hasattr(value, 'all'):
                                    attrs[key] = value
                            except Exception:
                                pass
                except Exception:
                    pass
                    
        except Exception as e:
            print(f"获取Attributes时出错: {str(e)}")
    
    # 显示Attributes
    if attrs:
        for key in sorted(attrs.keys()):
            value = attrs[key]
            formatted_value = format_value(value)
            print(f"  {key:<20}: {formatted_value}")
    else:
        print("无Attributes")

def test_attributes_listing():
    """测试attributes列出功能"""
    print("=== 测试Attributes列出功能 ===")
    
    # 创建测试对象
    obj = MockObject("测试角色")
    
    # 调用改进后的函数
    list_attributes_only(obj)
    
    print("\n=== 验证原始数据 ===")
    # 验证原始数据
    all_attrs = obj.attributes.all()
    print(f"通过.all()方法获取到 {len(all_attrs)} 个属性:")
    for attr in all_attrs:
        print(f"  {attr.key}: {attr.value}")

if __name__ == "__main__":
    test_attributes_listing()