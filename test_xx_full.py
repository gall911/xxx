#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
完整测试xx命令的脚本
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, '/home/gg/xxx')

# 模拟Evennia的部分功能
class MockObject:
    def __init__(self, key="test_obj"):
        self.key = key
        self.name = key
        self.id = 1
        self.dbref = "#1"
        self.pk = 1
        self.typename = "Character"
        self.is_connected = True
        self.has_account = 1
        self.is_superuser = True
        self.location = "测试地点"
        self.home = "测试之家"
        self.date_created = "2025-01-01"
        self.db = MockDB()
        self.ndb = MockNDB()
        self.attributes = MockAttributes()

class MockAttribute:
    def __init__(self, key, value):
        self.key = key
        self.value = value

class MockDB:
    def __init__(self):
        self.test_attr = "db_test_value"
        self.hp = 100
        self.mp = 50
    
    def all(self):
        return [MockAttribute("test_attr", "db_test_value"), MockAttribute("hp", 100), MockAttribute("mp", 50)]
    
    def get(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        return None

class MockNDB:
    def __init__(self):
        self.temp_attr = "ndb_test_value"
        self.status = "active"
    
    def all(self):
        return [MockAttribute("temp_attr", "ndb_test_value"), MockAttribute("status", "active")]

class MockAttributes:
    def __init__(self):
        self._attrs = {
            "strength": 10,
            "dexterity": 12,
            "intelligence": 15,
            "custom_attr": "自定义属性值"
        }
    
    def all(self):
        return [MockAttribute(key, value) for key, value in self._attrs.items()]

# 模拟Django模型
class MockModel:
    class _meta:
        pass

# 模拟消息输出
messages = []

def mock_msg(text):
    messages.append(text)
    print(text)

# 模拟format_value函数
def format_value(value):
    """
    格式化属性值用于显示（简化版）
    """
    # 处理None值
    if value is None:
        return "|xNone|n"
    
    # 处理布尔值
    if isinstance(value, bool):
        return "|gTrue|n" if value else "|rFalse|n"
    
    # 处理字符串，特别是多行字符串
    if isinstance(value, str):
        # 如果是多行字符串，只显示前几行并添加省略号
        lines = value.split('\n')
        if len(lines) > 5:
            display_lines = lines[:5]
            # 截断过长的行
            display_lines = [line[:100] + ("..." if len(line) > 100 else "") for line in display_lines]
            return "|w'''|n" + '\n'.join(display_lines) + "\n  |x... (省略了{}行)|n".format(len(lines) - 5) + "|w'''|n"
        elif len(lines) > 1:
            # 截断过长的多行字符串
            if any(len(line) > 100 for line in lines):
                shortened_lines = [line[:100] + ("..." if len(line) > 100 else "") for line in lines]
                return "|w'''|n" + '\n'.join(shortened_lines) + "|w'''|n"
            else:
                return "|w'''|n" + value + "|w'''|n"
        else:
            # 截断过长的单行字符串
            if len(value) > 100:
                return f"|w'{value[:100]}...'|n"
            else:
                return f"|w'{value}'|n"
    
    # 处理列表和元组
    if isinstance(value, (list, tuple)):
        if len(value) > 10:
            # 只显示前10个元素
            items = []
            for item in value[:10]:
                formatted_item = repr(item)
                if len(formatted_item) > 50:
                    formatted_item = formatted_item[:50] + "..."
                items.append(formatted_item)
            return f"[{', '.join(items)}, |x... (省略了{len(value) - 10}个元素)|n]"
        else:
            items = []
            for item in value:
                formatted_item = repr(item)
                if len(formatted_item) > 50:
                    formatted_item = formatted_item[:50] + "..."
                items.append(formatted_item)
            return f"[{', '.join(items)}]"
    
    # 处理字典
    if isinstance(value, dict):
        if len(value) > 5:
            # 只显示前5个键值对
            items = []
            for i, (k, v) in enumerate(value.items()):
                if i >= 5:
                    break
                formatted_k = repr(k)
                formatted_v = repr(v)
                if len(formatted_k) > 30:
                    formatted_k = formatted_k[:30] + "..."
                if len(formatted_v) > 30:
                    formatted_v = formatted_v[:30] + "..."
                items.append(f"{formatted_k}: {formatted_v}")
            return f"{{{', '.join(items)}, |x... (省略了{len(value) - 5}个键值对)|n}}"
        else:
            items = []
            for k, v in value.items():
                formatted_k = repr(k)
                formatted_v = repr(v)
                if len(formatted_k) > 30:
                    formatted_k = formatted_k[:30] + "..."
                if len(formatted_v) > 30:
                    formatted_v = formatted_v[:30] + "..."
                items.append(f"{formatted_k}: {formatted_v}")
            return f"{{{', '.join(items)}}}"
    
    # 处理模型对象
    try:
        if hasattr(value, '_meta') and isinstance(value._meta, type(MockModel._meta)):
            return f"|c<{value.__class__.__name__}: {getattr(value, 'key', getattr(value, 'name', str(value)))}>|n"
    except Exception:
        pass
    
    # 处理其他对象
    try:
        str_value = str(value)
        if len(str_value) > 100:
            return str_value[:100] + "..."
        else:
            return str_value
    except Exception:
        return f"|x<{type(value).__name__} object>|n"

# 模拟list_attributes_only方法
def list_attributes_only(target):
    """
    专门列出目标对象的Attributes
    """
    print(f"|c【{target.key}的Attributes】|n")
    
    # 获取Attributes
    attrs = {}
    if hasattr(target, "attributes") and target.attributes:
        try:
            # 尝试获取所有Attributes
            all_attrs = target.attributes.all()
            if all_attrs:
                for attr in all_attrs:
                    try:
                        attrs[attr.key] = attr.value
                    except:
                        pass
            else:
                # 如果all()方法不可用，尝试其他方式
                try:
                    # 遍历所有可能的属性
                    for key in dir(target.attributes):
                        if not key.startswith('_') and not callable(getattr(target.attributes, key, None)):
                            try:
                                value = getattr(target.attributes, key, None)
                                if value is not None:
                                    attrs[key] = value
                            except Exception:
                                pass
                except Exception:
                    pass
        except Exception as e:
            print(f"|r获取Attributes时出错: {str(e)}|n")
    
    # 显示Attributes
    if attrs:
        for key in sorted(attrs.keys()):
            value = attrs[key]
            formatted_value = format_value(value)
            print(f"  |y{key:<20}|n: {formatted_value}")
    else:
        print("|y无Attributes|n")

# 模拟_get_db_attributes方法
def _get_db_attributes(target):
    """获取db属性"""
    db_attrs = {}
    if hasattr(target, "db") and target.db:
        try:
            # 方法1: 使用.all()方法获取所有属性（如果可用）
            if hasattr(target.db, 'all'):
                try:
                    # 尝试获取所有属性
                    all_attrs = target.db.all()
                    if all_attrs:
                        for attr in all_attrs:
                            try:
                                db_attrs[attr.key] = attr.value
                            except:
                                pass
                except:
                    pass
            
            # 方法2: 使用.__dict__获取所有属性
            if hasattr(target.db, '__dict__'):
                db_dict = getattr(target.db, '__dict__', {})
                if db_dict and isinstance(db_dict, dict):
                    for key, value in db_dict.items():
                        if not key.startswith('_') and key not in ['_created', '_updated']:
                            db_attrs[key] = value
            
            # 方法3: 遍历所有属性
            for key in dir(target.db):
                if not key.startswith('_') and not callable(getattr(target.db, key, None)):
                    try:
                        # 特殊处理一些属性
                        if key in ['attributes', 'tags', 'locks']:
                            continue
                        db_attrs[key] = getattr(target.db, key, None)
                    except Exception:
                        pass
        except Exception as e:
            print(f"|r获取db属性时出错: {str(e)}|n")
    return db_attrs

# 模拟_get_ndb_attributes方法
def _get_ndb_attributes(target):
    """获取ndb属性"""
    ndb_attrs = {}
    if hasattr(target, "ndb") and target.ndb:
        try:
            # 方法1: 使用.all()方法获取所有属性（如果可用）
            if hasattr(target.ndb, 'all'):
                try:
                    # 尝试获取所有属性
                    all_attrs = target.ndb.all()
                    if all_attrs:
                        for attr in all_attrs:
                            try:
                                ndb_attrs[attr.key] = attr.value
                            except:
                                pass
                except:
                    pass
            
            # 方法2: 使用.__dict__获取所有属性
            if hasattr(target.ndb, '__dict__'):
                ndb_dict = getattr(target.ndb, '__dict__', {})
                if ndb_dict and isinstance(ndb_dict, dict):
                    for key, value in ndb_dict.items():
                        if not key.startswith('_'):
                            ndb_attrs[key] = value
            
            # 方法3: 遍历所有属性
            for key in dir(target.ndb):
                if not key.startswith('_') and not callable(getattr(target.ndb, key, None)):
                    try:
                        ndb_attrs[key] = getattr(target.ndb, key, None)
                    except Exception:
                        pass
        except Exception as e:
            print(f"|r获取ndb属性时出错: {str(e)}|n")
    return ndb_attrs

# 模拟_get_object_attributes方法
def _get_object_attributes(target):
    """获取对象本身的重要属性"""
    obj_attrs = {}
    # 定义应该显示的重要属性
    important_attrs = [
        'id', 'dbref', 'pk', 'key', 'name', 'typename',
        'is_connected', 'has_account', 'is_superuser',
        'account', 'location', 'home', 'destination',
        'date_created', 'db_date_created', 'lock_storage',
        'db_cmdset_storage', 'sessid', 'connection_time',
        'idle_time', 'cmdset_storage', 'typeclass_path'
    ]
    
    # 获取这些重要属性
    for key in important_attrs:
        if hasattr(target, key):
            try:
                attr_value = getattr(target, key, None)
                # 检查是否是可调用的对象或管理器
                if not callable(attr_value) and not hasattr(attr_value, 'all'):
                    obj_attrs[key] = attr_value
            except Exception:
                pass
    
    # 补充其他属性
    for key in dir(target):
        # 跳过特殊属性和可能导致问题的属性
        if (not key.startswith('_') and 
            key not in ['db', 'ndb', 'objects', 'attributes', 'tags', 'locks'] and
            key not in important_attrs):
            try:
                attr_value = getattr(target, key, None)
                # 检查是否是可调用的对象或管理器
                if not callable(attr_value) and not hasattr(attr_value, 'all'):
                    obj_attrs[key] = attr_value
            except Exception:
                # 忽略获取属性时的错误
                pass
                
    return obj_attrs

# 模拟list_all_attributes方法
def list_all_attributes(target):
    """
    列出目标对象的所有属性
    """
    print(f"|c【{target.key}的所有属性】|n")

    # 获取所有db属性
    db_attrs = _get_db_attributes(target)

    # 获取所有ndb属性
    ndb_attrs = _get_ndb_attributes(target)

    # 获取对象本身的重要属性
    obj_attrs = _get_object_attributes(target)

    # 显示db属性
    if db_attrs:
        print("\n|w【db属性】|n")
        # 优先显示重要属性
        priority_attrs = ['key', 'name', 'location', 'home', 'destination']
        
        # 先显示优先属性
        for key in priority_attrs:
            if key in db_attrs:
                value = db_attrs[key]
                formatted_value = format_value(value)
                print(f"  |y{key:<20}|n: {formatted_value}")
                
        # 再显示其他属性
        for key in sorted(db_attrs.keys()):
            if key not in priority_attrs:
                value = db_attrs[key]
                formatted_value = format_value(value)
                print(f"  |y{key:<20}|n: {formatted_value}")
    else:
        print("\n|w【db属性】|n: |y无|n")

    # 显示ndb属性
    if ndb_attrs:
        print("\n|w【ndb属性】|n")
        # 按键名排序
        for key in sorted(ndb_attrs.keys()):
            value = ndb_attrs[key]
            formatted_value = format_value(value)
            print(f"  |y{key:<20}|n: {formatted_value}")
    else:
        print("\n|w【ndb属性】|n: |y无|n")

    # 显示对象本身属性
    if obj_attrs:
        print("\n|w【对象属性】|n")
        # 优先显示重要属性
        priority_attrs = [
            'id', 'dbref', 'pk', 'typename',
            'is_connected', 'has_account', 'is_superuser',
            'account', 'location', 'home'
        ]
        
        # 先显示优先属性
        for key in priority_attrs:
            if key in obj_attrs:
                value = obj_attrs[key]
                formatted_value = format_value(value)
                print(f"  |y{key:<20}|n: {formatted_value}")
                
        # 再显示其他属性
        for key in sorted(obj_attrs.keys()):
            if key not in priority_attrs:
                value = obj_attrs[key]
                formatted_value = format_value(value)
                print(f"  |y{key:<20}|n: {formatted_value}")
                
    # 显示Attributes（如果有的话）
    if hasattr(target, "attributes") and target.attributes:
        try:
            attrs = {}
            all_attrs = target.attributes.all()
            if all_attrs:
                for attr in all_attrs:
                    try:
                        attrs[attr.key] = attr.value
                    except:
                        pass
            
            if attrs:
                print("\n|w【Attributes】|n")
                for key in sorted(attrs.keys()):
                    value = attrs[key]
                    formatted_value = format_value(value)
                    print(f"  |y{key:<20}|n: {formatted_value}")
        except Exception:
            pass

# 主测试函数
def main():
    print("=== 完整测试xx命令 ===\n")
    
    # 创建模拟对象
    target = MockObject("测试角色")
    
    # 测试list_all_attributes方法
    print("1. 测试list_all_attributes方法:")
    list_all_attributes(target)
    
    print("\n" + "="*50 + "\n")
    
    # 测试list_attributes_only方法
    print("2. 测试list_attributes_only方法 (-Attributes 参数):")
    list_attributes_only(target)

if __name__ == "__main__":
    main()