"""
超级all-in-one命令 - 用于查看和设置对象属性

用法:
  xx [对象名称] [属性名] [值] - 设置对象属性
  xx [对象名称] [属性名] - 查看对象属性
  xx [对象名称] - 列出对象所有属性

示例:
  xx hh - 列出hh的所有属性
  xx hh att - 查看hh的att属性
  xx hh hp 333 - 设置hh的hp属性为333
"""

from evennia.commands.default.muxcommand import MuxCommand as Command
from evennia import search_object


class CmdXX(Command):
    """
    超级all-in-one命令 - 用于查看和设置对象属性

    用法:
      xx [对象名称] [属性名] [值] - 设置对象属性
      xx [对象名称] [属性名] - 查看对象属性
      xx [对象名称] - 列出对象所有属性

    示例:
      xx hh - 列出hh的所有属性
      xx hh att - 查看hh的att属性
      xx hh hp 333 - 设置hh的hp属性为333
    """

    key = "xx"
    aliases = ["xx"]
    help_category = "修仙"

    def show_help(self):
        """显示命令帮助信息"""
        help_text = """
|c【xx命令帮助】|n

用法:
  |wxx [对象名称] [属性名] [值]|n - 设置对象属性
  |wxx [对象名称] [属性名]|n - 查看对象属性
  |wxx [对象名称]|n - 列出对象所有属性

示例:
  |wxx hh|n - 列出hh的所有属性
  |wxx hh att|n - 查看hh的att属性
  |wxx hh hp 333|n - 设置hh的hp属性为333
        """.strip()
        self.msg(help_text)

    def func(self):
        """命令执行函数"""
        # 获取命令参数
        args = self.args.strip()

        # 如果没有参数，显示帮助
        if not args:
            self.show_help()
            return

        # 分割参数
        parts = args.split()
        target_name = parts[0]

        # 查找目标对象
        target = self.search_for_object(target_name)
        if not target:
            self.msg(f"|r找不到对象: {target_name}|n")
            return

        # 如果只有对象名称，列出所有属性
        if len(parts) == 1:
            self.list_all_attributes(target)
            return

        # 如果有对象名称和属性名
        attr_name = parts[1]

        # 如果只有对象名称和属性名，显示属性值
        if len(parts) == 2:
            self.show_attribute(target, attr_name)
            return

        # 如果有对象名称、属性名和值，设置属性
        if len(parts) >= 3:
            value = " ".join(parts[2:])
            self.set_attribute(target, attr_name, value)
            return

    def search_for_object(self, target_name):
        """
        搜索目标对象

        Args:
            target_name: 对象名称

        Returns:
            找到的对象，如果没找到返回None
        """
        # 先尝试精确匹配
        obj = self.caller.search(target_name, global_search=True, use_nicks=True)
        if obj:
            return obj

        # 如果精确匹配失败，尝试模糊匹配
        results = search_object(target_name)

        if not results:
            return None

        # 如果只有一个结果，直接返回
        if len(results) == 1:
            return results[0]

        # 如果有多个结果，让用户选择
        self.msg(f"|y找到多个匹配对象:|n")
        for i, obj in enumerate(results, 1):
            self.msg(f"  {i}. {obj.key}")

        # 等待用户选择
        self.msg("|y请输入编号选择目标对象|n")
        return None

    def list_all_attributes(self, target):
        """
        列出目标对象的所有属性

        Args:
            target: 目标对象
        """
        self.msg(f"|c【{target.key}的所有属性】|n")

        # 获取所有db属性
        db_attrs = {}
        if hasattr(target, "db") and target.db:
            # 尝试多种方法获取db属性
            try:
                # 方法1: 使用.__dict__获取所有属性
                if hasattr(target.db, '__dict__'):
                    db_dict = getattr(target.db, '__dict__', {})
                    if db_dict and isinstance(db_dict, dict):
                        for key, value in db_dict.items():
                            if not key.startswith('_'):
                                db_attrs[key] = value
                # 方法2: 遍历所有属性
                else:
                    for key in dir(target.db):
                        if not key.startswith('_') and not callable(getattr(target.db, key, None)):
                            try:
                                db_attrs[key] = getattr(target.db, key, None)
                            except Exception:
                                pass
            except Exception as e:
                self.msg(f"|r获取db属性时出错: {str(e)}|n")

        # 获取所有ndb属性
        ndb_attrs = {}
        if hasattr(target, "ndb") and target.ndb:
            # 尝试多种方法获取ndb属性
            try:
                # 方法1: 使用.__dict__获取所有属性
                if hasattr(target.ndb, '__dict__'):
                    ndb_dict = getattr(target.ndb, '__dict__', {})
                    if ndb_dict and isinstance(ndb_dict, dict):
                        for key, value in ndb_dict.items():
                            if not key.startswith('_'):
                                ndb_attrs[key] = value
                # 方法2: 遍历所有属性
                else:
                    for key in dir(target.ndb):
                        if not key.startswith('_') and not callable(getattr(target.ndb, key, None)):
                            try:
                                ndb_attrs[key] = getattr(target.ndb, key, None)
                            except Exception:
                                pass
            except Exception as e:
                self.msg(f"|r获取ndb属性时出错: {str(e)}|n")

        # 显示对象本身的属性
        obj_attrs = {}
        for key in dir(target):
            # 跳过特殊属性和可能导致问题的属性
            if not key.startswith('_') and key not in ['db', 'ndb', 'objects']:
                try:
                    attr_value = getattr(target, key, None)
                    # 检查是否是可调用的对象或管理器
                    if not callable(attr_value) and not hasattr(attr_value, 'all'):
                        obj_attrs[key] = attr_value
                except Exception:
                    # 忽略获取属性时的错误
                    pass

        # 显示db属性
        if db_attrs:
            self.msg("\n|w【db属性】|n")
            # 按键名排序
            for key in sorted(db_attrs.keys()):
                value = db_attrs[key]
                # 格式化显示
                formatted_value = self.format_value(value)
                self.msg(f"  |y{key}|n: {formatted_value}")
        else:
            self.msg("\n|w【db属性】|n: |y无|n")

        # 显示ndb属性
        if ndb_attrs:
            self.msg("\n|w【ndb属性】|n")
            # 按键名排序
            for key in sorted(ndb_attrs.keys()):
                value = ndb_attrs[key]
                # 格式化显示
                formatted_value = self.format_value(value)
                self.msg(f"  |y{key}|n: {formatted_value}")
        else:
            self.msg("\n|w【ndb属性】|n: |y无|n")

        # 显示对象本身属性
        if obj_attrs:
            self.msg("\n|w【对象属性】|n")
            # 按键名排序
            for key in sorted(obj_attrs.keys()):
                value = obj_attrs[key]
                # 格式化显示
                formatted_value = self.format_value(value)
                self.msg(f"  |y{key}|n: {formatted_value}")

    def format_value(self, value):
        """
        格式化属性值用于显示

        Args:
            value: 要格式化的值

        Returns:
            格式化后的字符串
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
                return "|w'''|n" + '\n'.join(lines[:5]) + "\n  |x... (省略了{}行)|n".format(len(lines) - 5) + "|w'''|n"
            elif len(lines) > 1:
                return "|w'''|n" + value + "|w'''|n"
            else:
                return f"|w'{value}'|n"
        
        # 处理列表和元组
        if isinstance(value, (list, tuple)):
            if len(value) > 10:
                # 只显示前10个元素
                items = [repr(item) for item in value[:10]]
                return f"[{', '.join(items)}, |x... (省略了{len(value) - 10}个元素)|n]"
            else:
                items = [repr(item) for item in value]
                return f"[{', '.join(items)}]"
        
        # 处理字典
        if isinstance(value, dict):
            if len(value) > 5:
                # 只显示前5个键值对
                items = [f"{repr(k)}: {repr(v)}" for i, (k, v) in enumerate(value.items()) if i < 5]
                return f"{{{', '.join(items)}, |x... (省略了{len(value) - 5}个键值对)|n}}"
            else:
                items = [f"{repr(k)}: {repr(v)}" for k, v in value.items()]
                return f"{{{', '.join(items)}}}"
        
        # 处理其他对象
        try:
            return str(value)
        except Exception:
            return f"|x<{type(value).__name__} object>|n"

    def show_attribute(self, target, attr_name):
        """
        显示目标对象的指定属性值

        Args:
            target: 目标对象
            attr_name: 属性名
        """
        # 尝试从对象本身获取属性
        if hasattr(target, attr_name):
            try:
                value = getattr(target, attr_name)
                # 检查是否是可调用的对象或管理器
                if not callable(value) and not hasattr(value, 'all'):
                    formatted_value = self.format_value(value)
                    self.msg(f"|c【{target.key}的{attr_name}】|n: {formatted_value}")
                    return
            except Exception:
                pass

        # 尝试从db获取属性
        if hasattr(target, "db") and target.db:
            try:
                if hasattr(target.db, attr_name):
                    value = getattr(target.db, attr_name)
                    formatted_value = self.format_value(value)
                    self.msg(f"|c【{target.key}的{attr_name}】|n: {formatted_value}")
                    return
            except Exception:
                pass

        # 尝试从ndb获取属性
        if hasattr(target, "ndb") and target.ndb:
            try:
                if hasattr(target.ndb, attr_name):
                    value = getattr(target.ndb, attr_name)
                    formatted_value = self.format_value(value)
                    self.msg(f"|c【{target.key}的{attr_name}】|n: {formatted_value}")
                    return
            except Exception:
                pass

        # 如果都没找到
        self.msg(f"|r找不到属性: {attr_name}|n")

    def set_attribute(self, target, attr_name, value):
        """
        设置目标对象的属性值

        Args:
            target: 目标对象
            attr_name: 属性名
            value: 属性值
        """
        try:
            # 尝试转换为适当的数据类型
            # 先尝试整数
            try:
                value = int(value)
            except ValueError:
                # 如果不是整数，尝试浮点数
                try:
                    value = float(value)
                except ValueError:
                    # 如果不是浮点数，保持为字符串
                    # 处理布尔值
                    if value.lower() in ["true", "false"]:
                        value = value.lower() == "true"
                    # 处理None
                    elif value.lower() == "none":
                        value = None

            # 设置db属性 - 使用正确的方法
            if hasattr(target, "db"):
                try:
                    setattr(target.db, attr_name, value)
                    self.msg(f"|g已设置|n |c{target.key}|n 的 |c{attr_name}|n 为 |c{self.format_value(value)}|n")
                    return
                except Exception as e:
                    # 如果setattr失败，尝试直接赋值
                    try:
                        if not hasattr(target.db, '__dict__'):
                            setattr(target.db, '__dict__', {})
                        target.db.__dict__[attr_name] = value
                        self.msg(f"|g已设置|n |c{target.key}|n 的 |c{attr_name}|n 为 |c{self.format_value(value)}|n")
                        return
                    except Exception:
                        pass

            # 如果对象没有db属性，提示错误
            self.msg(f"|r无法设置属性: {attr_name}|n")

        except Exception as e:
            self.msg(f"|r设置属性时发生错误: {str(e)}|n")