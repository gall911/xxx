"""
超级all-in-one命令 - 用于查看和设置对象属性

用法:
  xx [对象名称] [属性名] [值] - 设置对象属性
  xx [对象名称] [属性名] - 查看对象属性
  xx [对象名称] - 列出对象所有属性
  xx room [房间名] desc -text - 从模板设置房间描述
  xx room - 列出所有房间

示例:
  xx hh - 列出hh的所有属性
  xx hh att - 查看hh的att属性
  xx hh hp 333 - 设置hh的hp属性为333
  xx room 我的房间 desc -text - 从text.yaml模板设置房间描述
  xx room - 列出所有房间
"""

from evennia.commands.default.muxcommand import MuxCommand as Command
from evennia import search_object
from world.templates.loader import TemplateLoader
from world.templates.room_desc_loader import RoomDescTemplateLoader
from utils.theme_utils import color_room_name


class CmdXX(Command):
    """
    超级all-in-one命令 - 用于查看和设置对象属性

    用法:
      xx [对象名称] [属性名] [值] - 设置对象属性
      xx [对象名称] [属性名] - 查看对象属性
      xx [对象名称] - 列出对象所有属性
      xx room - 列出所有房间

    示例:
      xx hh - 列出hh的所有属性
      xx hh att - 查看hh的att属性
      xx hh hp 333 - 设置hh的hp属性为333
      xx room - 列出所有房间
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
  |wxx room [房间名] desc -text|n - 从模板设置房间描述
  |wxx room|n - 列出所有房间

示例:
  |wxx hh|n - 列出hh的所有属性
  |wxx hh att|n - 查看hh的att属性
  |wxx hh hp 333|n - 设置hh的hp属性为333
  |wxx room 我的房间 desc -text|n - 从text.yaml模板设置房间描述
  |wxx room|n - 列出所有房间
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
        
        # 检查是否是列出所有房间的命令
        if parts[0] == "room" and len(parts) == 1:
            self.list_all_rooms()
            return
        
        # 检查是否是room命令 (支持两种格式: "xx room [房间名] desc -text" 或 "xx [房间名] desc -text")
        if (parts[0] == "room" and len(parts) >= 4) or (len(parts) >= 3 and parts[1] == "desc" and parts[2].startswith("-")):
            # 处理room命令
            if parts[0] == "room":
                # 格式: xx room [房间名] desc -text
                if parts[2] == "desc" and parts[3].startswith("-"):
                    room_name = parts[1]
                    template_name = parts[3][1:]  # 去掉前面的"-"
                else:
                    self.msg("|r命令格式错误。正确格式: xx room [房间名] desc -text|n")
                    return
            else:
                # 格式: xx [房间名] desc -text
                if parts[1] == "desc" and parts[2].startswith("-"):
                    room_name = parts[0]
                    template_name = parts[2][1:]  # 去掉前面的"-"
                else:
                    self.msg("|r命令格式错误。正确格式: xx [房间名] desc -text|n")
                    return
                
            # 查找房间
            room = self.caller.search(room_name, global_search=True, use_nicks=True)
            if not room:
                self.msg(f"|r找不到房间: {room_name}|n")
                return
                
            # 从模板获取描述（使用新的RoomDescTemplateLoader）
            description = RoomDescTemplateLoader.get_room_description(template_name)
            
            # 设置房间描述
            if hasattr(room, "db"):
                room.db.desc = description
                self.msg(f"|g已成功设置房间|n |c{room_name}|n |g的描述为:|n\n{description}")
            else:
                self.msg(f"|r无法设置房间描述: {room_name}|n")
            return

        target_name = parts[0]

        # 查找目标对象
        target = self.caller.search(target_name, global_search=True, use_nicks=True)
        if not target:
            self.msg(f"|r找不到对象: {target_name}|n")
            return

        # 如果只有对象名称，列出所有属性
        if len(parts) == 1:
            self.list_all_attributes(target)
            return

        # 如果有对象名称和属性名，显示属性值
        attr_name = parts[1]
        if len(parts) == 2:
            self.show_attribute(target, attr_name)
            return

        # 如果有对象名称、属性名和值，设置属性
        if len(parts) >= 3:
            value = " ".join(parts[2:])
            self.set_attribute(target, attr_name, value)
            return

    def list_all_rooms(self):
        """列出所有房间"""
        # 搜索所有房间对象
        rooms = search_object("", typeclass="typeclasses.rooms.Room")
        
        if not rooms:
            # 尝试另一种搜索方式
            try:
                from typeclasses.rooms import Room
                rooms = Room.objects.all()
                if not rooms:
                    self.msg("没有找到任何房间。")
                    return
            except Exception as e:
                self.msg(f"没有找到任何房间。")
                return
            
        # 按房间ID排序
        rooms = sorted(rooms, key=lambda r: r.id)
        
        # 构建房间列表
        room_list = []
        for room in rooms:
            # 使用lc标签使房间名可点击，使用look命令查看房间信息
            clickable_name = f"|lc@tel #{room.id}|lt{color_room_name(room.key)}|le"
            room_list.append(f"{room.id:4d} - {clickable_name}")
            
        # 发送房间列表给用户
        header = "|c【房间列表】|n"
        footer = f"总共找到 {len(rooms)} 个房间。"
        
        # 分页显示，每页20个房间
        page_size = 20
        total_pages = (len(room_list) + page_size - 1) // page_size
        
        if "page" in self.switches:
            try:
                page_num = int(self.switches["page"])
            except (ValueError, TypeError):
                page_num = 1
        else:
            page_num = 1
            
        if page_num < 1:
            page_num = 1
        elif page_num > total_pages:
            page_num = total_pages
            
        start_idx = (page_num - 1) * page_size
        end_idx = min(start_idx + page_size, len(room_list))
        current_page = room_list[start_idx:end_idx]
        
        # 构建输出
        output = [header]
        output.extend(current_page)
        output.append(f"{footer} (第 {page_num}/{total_pages} 页)")
        output.append("|g提示: 点击房间名可以查看房间信息|n")
        
        if total_pages > 1:
            output.append("使用 xx room/page <页码> 来查看其他页")
            
        self.msg("\n".join(output))

    def list_all_attributes(self, target):
        """
        列出目标对象的所有属性

        Args:
            target: 目标对象
        """
        self.msg(f"|c【{target.key}的所有属性】|n")

        # 显示对象的基本属性
        basic_attrs = ['key', 'name', 'location', 'home', 'destination']
        for attr_name in basic_attrs:
            if hasattr(target, attr_name):
                value = getattr(target, attr_name, None)
                formatted_value = self.format_value(value)
                self.msg(f"  |y{attr_name:<15}|n: {formatted_value}")

        # 显示db属性
        if hasattr(target, "db") and target.db:
            self.msg("\n|w【db属性】|n")
            try:
                # 获取db中的所有属性
                if hasattr(target.db, '__dict__'):
                    db_dict = getattr(target.db, '__dict__', {})
                    for key, value in db_dict.items():
                        if not key.startswith('_') and key not in ['_created', '_updated']:
                            formatted_value = self.format_value(value)
                            self.msg(f"  |y{key:<15}|n: {formatted_value}")
            except Exception as e:
                self.msg(f"|r获取db属性时出错: {str(e)}|n")

        # 显示Attributes
        if hasattr(target, "attributes") and target.attributes:
            self.msg("\n|w【Attributes】|n")
            try:
                # 获取Attributes
                attrs = target.attributes.all()
                if attrs:
                    for attr in attrs:
                        try:
                            formatted_value = self.format_value(attr.value)
                            self.msg(f"  |y{attr.key:<15}|n: {formatted_value}")
                        except:
                            pass
            except Exception as e:
                self.msg(f"|r获取Attributes时出错: {str(e)}|n")

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
                # 尝试通过属性访问
                try:
                    value = target.db.get(attr_name)
                    formatted_value = self.format_value(value)
                    self.msg(f"|c【{target.key}的{attr_name}】|n: {formatted_value}")
                    return
                except:
                    pass
            except Exception:
                pass

        # 尝试从Attributes获取属性
        if hasattr(target, "attributes") and target.attributes:
            try:
                value = target.attributes.get(attr_name)
                if value is not None:
                    formatted_value = self.format_value(value)
                    self.msg(f"|c【{target.key}的{attr_name}】|n: {formatted_value}")
                    return
            except Exception:
                pass

        # 如果都没找到
        self.msg(f"|r找不到属性: {attr_name}|n")

    def set_attribute(self, target, attr_name, value_str):
        """
        设置目标对象的属性值

        Args:
            target: 目标对象
            attr_name: 属性名
            value_str: 属性值字符串
        """
        try:
            # 尝试转换为适当的数据类型
            value = self.parse_value(value_str)

            # 设置db属性 - 使用正确的方法
            if hasattr(target, "db"):
                try:
                    # 使用add方法设置属性
                    target.db.add(attr_name, value)
                    self.msg(f"|g已设置|n |c{target.key}|n 的 |c{attr_name}|n 为 |c{self.format_value(value)}|n")
                    return
                except Exception:
                    # 如果add失败，尝试setattr
                    try:
                        setattr(target.db, attr_name, value)
                        self.msg(f"|g已设置|n |c{target.key}|n 的 |c{attr_name}|n 为 |c{self.format_value(value)}|n")
                        return
                    except Exception:
                        pass

            # 如果对象没有db属性，提示错误
            self.msg(f"|r无法设置属性: {attr_name}|n")

        except Exception as e:
            self.msg(f"|r设置属性时发生错误: {str(e)}|n")

    def parse_value(self, value_str):
        """
        解析字符串值为适当的数据类型

        Args:
            value_str: 字符串值

        Returns:
            解析后的值
        """
        # 处理None
        if value_str.lower() == "none":
            return None
            
        # 处理布尔值
        if value_str.lower() == "true":
            return True
        if value_str.lower() == "false":
            return False

        # 尝试整数
        try:
            return int(value_str)
        except ValueError:
            pass

        # 尝试浮点数
        try:
            return float(value_str)
        except ValueError:
            pass

        # 默认返回字符串
        return value_str

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
        
        # 处理字符串
        if isinstance(value, str):
            # 截断过长的字符串
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
        
        # 处理其他对象
        try:
            str_value = str(value)
            if len(str_value) > 100:
                return str_value[:100] + "..."
            else:
                return str_value
        except Exception:
            return f"|x<{type(value).__name__} object>|n"