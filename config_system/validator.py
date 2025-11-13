"""
配置验证模块

提供配置文件内容的验证功能，确保配置符合预期的格式、类型和取值范围。
"""

import re
from typing import Any, Dict, List, Optional, Union

class ValidationError(Exception):
    """配置验证错误"""
    pass

class ValidationRule:
    """验证规则基类"""

    def __init__(self, required: bool = False, description: str = ""):
        self.required = required
        self.description = description

    def validate(self, value: Any) -> bool:
        """验证值是否符合规则"""
        raise NotImplementedError

    def get_error_message(self, key: str, value: Any) -> str:
        """获取错误消息"""
        return f"配置项 '{key}' 的值 '{value}' 不符合验证规则"

class TypeRule(ValidationRule):
    """类型验证规则"""

    def __init__(self, expected_type: Union[type, str], **kwargs):
        super().__init__(**kwargs)
        if isinstance(expected_type, str):
            # 将字符串类型转换为实际类型
            self.expected_type = {
                'str': str,
                'int': int,
                'float': float,
                'bool': bool,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set
            }.get(expected_type.lower(), str)
        else:
            self.expected_type = expected_type

    def validate(self, value: Any) -> bool:
        return isinstance(value, self.expected_type)

    def get_error_message(self, key: str, value: Any) -> str:
        return f"配置项 '{key}' 应为 {self.expected_type.__name__} 类型，实际为 {type(value).__name__}"

class RangeRule(ValidationRule):
    """范围验证规则"""

    def __init__(self, min_val: Optional[float] = None, max_val: Optional[float] = None, **kwargs):
        super().__init__(**kwargs)
        self.min_val = min_val
        self.max_val = max_val

    def validate(self, value: Any) -> bool:
        try:
            num_val = float(value)
            if self.min_val is not None and num_val < self.min_val:
                return False
            if self.max_val is not None and num_val > self.max_val:
                return False
            return True
        except (ValueError, TypeError):
            return False

    def get_error_message(self, key: str, value: Any) -> str:
        parts = []
        if self.min_val is not None:
            parts.append(f"最小值为 {self.min_val}")
        if self.max_val is not None:
            parts.append(f"最大值为 {self.max_val}")

        constraint = " 和 ".join(parts)
        return f"配置项 '{key}' 的值 '{value}' 超出范围，{constraint}"

class LengthRule(ValidationRule):
    """长度验证规则"""

    def __init__(self, min_len: Optional[int] = None, max_len: Optional[int] = None, **kwargs):
        super().__init__(**kwargs)
        self.min_len = min_len
        self.max_len = max_len

    def validate(self, value: Any) -> bool:
        try:
            length = len(value)
            if self.min_len is not None and length < self.min_len:
                return False
            if self.max_len is not None and length > self.max_len:
                return False
            return True
        except TypeError:
            return False

    def get_error_message(self, key: str, value: Any) -> str:
        parts = []
        if self.min_len is not None:
            parts.append(f"最小长度为 {self.min_len}")
        if self.max_len is not None:
            parts.append(f"最大长度为 {self.max_len}")

        constraint = " 和 ".join(parts)
        return f"配置项 '{key}' 的长度超出范围，{constraint}"

class RegexRule(ValidationRule):
    """正则表达式验证规则"""

    def __init__(self, pattern: str, **kwargs):
        super().__init__(**kwargs)
        self.pattern = pattern
        self.regex = re.compile(pattern)

    def validate(self, value: Any) -> bool:
        if not isinstance(value, str):
            return False
        return bool(self.regex.match(value))

    def get_error_message(self, key: str, value: Any) -> str:
        return f"配置项 '{key}' 的值 '{value}' 不符合正则表达式模式: {self.pattern}"

class EnumRule(ValidationRule):
    """枚举值验证规则"""

    def __init__(self, valid_values: List[Any], **kwargs):
        super().__init__(**kwargs)
        self.valid_values = valid_values

    def validate(self, value: Any) -> bool:
        return value in self.valid_values

    def get_error_message(self, key: str, value: Any) -> str:
        return f"配置项 '{key}' 的值 '{value}' 不是有效值，有效值为: {', '.join(map(str, self.valid_values))}"

class ConfigValidator:
    """配置验证器"""

    def __init__(self):
        self.rules: Dict[str, List[ValidationRule]] = {}

    def add_rule(self, config_name: str, key_path: str, rule: ValidationRule):
        """添加验证规则"""
        full_path = f"{config_name}.{key_path}"
        if full_path not in self.rules:
            self.rules[full_path] = []
        self.rules[full_path].append(rule)

    def add_type_rule(self, config_name: str, key_path: str, expected_type: Union[type, str], **kwargs):
        """添加类型验证规则"""
        self.add_rule(config_name, key_path, TypeRule(expected_type, **kwargs))

    def add_range_rule(self, config_name: str, key_path: str, min_val: Optional[float] = None, 
                      max_val: Optional[float] = None, **kwargs):
        """添加范围验证规则"""
        self.add_rule(config_name, key_path, RangeRule(min_val, max_val, **kwargs))

    def add_length_rule(self, config_name: str, key_path: str, min_len: Optional[int] = None, 
                        max_len: Optional[int] = None, **kwargs):
        """添加长度验证规则"""
        self.add_rule(config_name, key_path, LengthRule(min_len, max_len, **kwargs))

    def add_regex_rule(self, config_name: str, key_path: str, pattern: str, **kwargs):
        """添加正则表达式验证规则"""
        self.add_rule(config_name, key_path, RegexRule(pattern, **kwargs))

    def add_enum_rule(self, config_name: str, key_path: str, valid_values: List[Any], **kwargs):
        """添加枚举值验证规则"""
        self.add_rule(config_name, key_path, EnumRule(valid_values, **kwargs))

    def validate_config(self, config_name: str, config_data: Dict[str, Any]) -> List[str]:
        """验证配置数据，返回错误消息列表"""
        errors = []

        # 检查所有规则
        for full_path, rules in self.rules.items():
            if not full_path.startswith(f"{config_name}."):
                continue

            key_path = full_path[len(f"{config_name}."):]
            keys = key_path.split('.')

            # 导航到目标键
            current = config_data
            target_key = None

            try:
                for key in keys[:-1]:
                    current = current[key]
                target_key = keys[-1]
            except (KeyError, TypeError):
                # 路径不存在，检查是否是必需的
                for rule in rules:
                    if rule.required:
                        errors.append(f"必需的配置项 '{key_path}' 缺失")
                continue

            # 检查目标键是否存在
            if target_key not in current:
                for rule in rules:
                    if rule.required:
                        errors.append(f"必需的配置项 '{key_path}' 缺失")
                continue

            # 验证值
            value = current[target_key]
            for rule in rules:
                if not rule.validate(value):
                    errors.append(rule.get_error_message(key_path, value))

        return errors

    def load_rules_from_dict(self, rules_dict: Dict[str, Dict]):
        """从字典加载验证规则"""
        for config_name, config_rules in rules_dict.items():
            for key_path, rule_specs in config_rules.items():
                for rule_spec in rule_specs:
                    rule_type = rule_spec.get("type")
                    rule_params = {k: v for k, v in rule_spec.items() if k != "type"}

                    if rule_type == "type":
                        self.add_type_rule(config_name, key_path, **rule_params)
                    elif rule_type == "range":
                        self.add_range_rule(config_name, key_path, **rule_params)
                    elif rule_type == "length":
                        self.add_length_rule(config_name, key_path, **rule_params)
                    elif rule_type == "regex":
                        self.add_regex_rule(config_name, key_path, **rule_params)
                    elif rule_type == "enum":
                        self.add_enum_rule(config_name, key_path, **rule_params)
                    else:
                        raise ValueError(f"未知的验证规则类型: {rule_type}")

# 全局配置验证器实例
_config_validator: Optional[ConfigValidator] = None

def get_config_validator() -> ConfigValidator:
    """获取全局配置验证器实例"""
    global _config_validator
    if _config_validator is None:
        _config_validator = ConfigValidator()
    return _config_validator
