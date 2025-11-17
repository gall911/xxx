#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试xx命令的脚本
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

# 测试format_value函数
def test_format_value():
    print("=== 测试format_value函数 ===")
    
    # 测试None值
    print("None值:", format_value(None))
    
    # 测试布尔值
    print("布尔值True:", format_value(True))
    print("布尔值False:", format_value(False))
    
    # 测试字符串
    print("短字符串:", format_value("hello"))
    print("长字符串:", format_value("这是一个很长的字符串，超过了一百个字符的限制，所以我们需要截断它以适应显示要求。这是一个很长的字符串，超过了一百个字符的限制，所以我们需要截断它以适应显示要求。"))
    
    # 测试多行字符串
    multiline = "第一行\n第二行\n第三行\n第四行\n第五行\n第六行\n第七行"
    print("多行字符串:", format_value(multiline))
    
    # 测试列表
    short_list = [1, 2, 3, 4, 5]
    long_list = list(range(15))
    print("短列表:", format_value(short_list))
    print("长列表:", format_value(long_list))
    
    # 测试字典
    short_dict = {"a": 1, "b": 2, "c": 3}
    long_dict = {f"key{i}": f"value{i}" for i in range(10)}
    print("短字典:", format_value(short_dict))
    print("长字典:", format_value(long_dict))
    
    # 测试模型对象
    model_obj = MockModel()
    print("模型对象:", format_value(model_obj))

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

def test_list_attributes_only():
    print("\n=== 测试list_attributes_only函数 ===")
    
    # 创建模拟对象
    target = MockObject("测试角色")
    
    # 模拟消息输出
    messages = []
    
    def mock_msg(text):
        messages.append(text)
        print(text)
    
    # 模拟list_attributes_only方法
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

def test_get_attributes_methods():
    print("\n=== 测试_get_db_attributes和_get_ndb_attributes方法 ===")
    
    # 创建模拟对象
    target = MockObject("测试角色")
    
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
    
    # 测试获取db属性
    db_attrs = _get_db_attributes(target)
    print("DB属性:")
    for key, value in db_attrs.items():
        print(f"  {key}: {format_value(value)}")
    
    # 测试获取ndb属性
    ndb_attrs = _get_ndb_attributes(target)
    print("\nNDB属性:")
    for key, value in ndb_attrs.items():
        print(f"  {key}: {format_value(value)}")

if __name__ == "__main__":
    test_format_value()
    test_list_attributes_only()
    test_get_attributes_methods()