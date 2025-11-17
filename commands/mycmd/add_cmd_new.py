
"""
Add命令模块

实现add命令的各种功能
"""

import os
from evennia import Command
from evennia import create_object
import yaml


# 简化版本，避免导入问题
class CmdAdd(Command):
    """
    添加各种游戏元素的命令

    用法:
        add room --<模板名>           # 使用模板名作为房间名
        add room <房间名> <模板名>     # 指定房间名和模板名
        add room <房间名>             # 只指定房间名，使用默认模板(base)
        add rooms <模板文件名>        # 批量创建房间

    示例:
        add room --base              # 创建名为"base"的房间，使用base模板
        add room 山洞 base           # 创建名为"山洞"的房间，使用base模板
        add room 测试房间            # 创建名为"测试房间"的房间，使用base模板
        add rooms mdl               # 从world/templates/rooms/mdl.yaml批量创建房间
    """

    key = "add"
    aliases = []
    locks = "cmd:perm(Builder)"
    help_category = "Building"

    def func(self):
        """命令主函数"""
        # 解析参数
        args = self.args.strip().split()

        if not args:
            self.caller.msg("用法: add room [--<模板名>|<房间名> <模板名>|<房间名>] 或 add rooms <模板文件名>")
            return

        subcommand = args[0].lower()

        if subcommand == "room":
            self.handle_room_command(args[1:])
        elif subcommand == "rooms":
            if len(args) < 2:
                self.caller.msg("用法: add rooms <模板文件名>")
                return
            template_file = args[1]
            self.create_rooms_from_template(template_file)
        else:
            self.caller.msg(f"未知的子命令: {subcommand}")

    def handle_room_command(self, args):
        """处理room子命令"""
        if not args:
            self.caller.msg("用法: add room [--<模板名>|<房间名> <模板名>|<房间名>]")
            return

        # 检查是否是 --<模板名> 格式
        if args[0].startswith("--"):
            template_name = args[0][2:]  # 去掉前缀 --
            room_name = template_name    # 使用模板名作为房间名
            self.create_room(room_name, template_name)
        # 检查是否有两个参数 (房间名和模板名)
        elif len(args) >= 2:
            room_name = args[0]
            template_name = args[1]
            self.create_room(room_name, template_name)
        # 只有一个参数 (仅房间名)，使用默认模板
        else:
            room_name = args[0]
            template_name = "base"  # 默认模板
            self.create_room(room_name, template_name)

    def create_room(self, room_name, template_name):
        """创建单个房间"""
        try:
            # 导入RoomLoader
            from world.templates.room_loader import RoomLoader

            # 创建房间
            new_room = create_object("typeclasses.rooms.Room", key=room_name)

            self.caller.msg(f"正在使用RoomLoader加载模板: {template_name}")

            # 使用RoomLoader加载模板数据
            try:
                template_data = RoomLoader.load(template_name)

                # 检查是否为批量房间模板
                if isinstance(template_data, dict) and 'rooms' in template_data:
                    # 如果是批量模板，使用第一个房间的数据作为模板
                    first_room_key = list(template_data['rooms'].keys())[0]
                    room_template = template_data['rooms'][first_room_key]
                    self.caller.msg(f"检测到批量房间模板，使用第一个房间 '{first_room_key}' 作为模板")
                else:
                    # 单个房间模板
                    room_template = template_data

                # 应用模板中的描述
                if 'desc' in room_template:
                    new_room.db.desc = room_template['desc']
                    self.caller.msg(f"已应用描述: {room_template['desc'][:50]}...")
                # 应用模板中的标签
                if 'tags' in room_template and isinstance(room_template['tags'], list):
                    for tag in room_template['tags']:
                        new_room.tags.add(tag)
                    self.caller.msg(f"已应用标签: {room_template['tags']}")
                # 应用模板中的属性
                if 'attributes' in room_template and isinstance(room_template['attributes'], dict):
                    for key, value in room_template['attributes'].items():
                        # 特殊处理布尔值和数字
                        if isinstance(value, str):
                            if value.lower() == "true":
                                value = True
                            elif value.lower() == "false":
                                value = False
                            elif value.isdigit():
                                value = int(value)
                            elif value.replace('.', '', 1).isdigit():
                                value = float(value)

                        new_room.attributes.add(key, value)
                    self.caller.msg(f"已应用属性: {room_template['attributes']}")
                # 应用key字段（如果存在且不同于房间名）
                if 'key' in room_template and room_template['key'] != room_name:
                    # key已经在创建时设置为room_name，这里可以选择是否覆盖
                    pass
            except FileNotFoundError:
                # 如果模板不存在，使用默认描述
                new_room.db.desc = f"这是一个通过模板 '{template_name}' 创建的房间: {room_name}"
                self.caller.msg(f"模板文件不存在，使用默认描述")

            self.caller.msg(f"成功创建房间 '{room_name}' 并应用模板 '{template_name}'")

        except Exception as e:
            self.caller.msg(f"创建房间时出错: {e}")
            import traceback
            self.caller.msg(f"错误详情: {traceback.format_exc()}")

    def create_rooms_from_template(self, template_file):
        """从模板文件批量创建多个房间"""
        try:
            # 导入RoomLoader
            from world.templates.room_loader import RoomLoader

            self.caller.msg(f"正在使用RoomLoader加载模板文件: {template_file}")

            # 使用RoomLoader加载模板数据
            template_data = RoomLoader.load(template_file)

            # 检查是否为批量房间格式
            if not isinstance(template_data, dict) or 'rooms' not in template_data:
                self.caller.msg("模板文件格式不正确，应包含'rooms'字段")
                return

            rooms_data = template_data['rooms']
            created_rooms = {}
            room_objects = {}

            self.caller.msg(f"开始创建 {len(rooms_data)} 个房间...")

            # 第一步：创建所有房间对象
            for room_key, room_info in rooms_data.items():
                try:
                    # 使用room_key作为房间名，如果没有指定则使用room_info中的key
                    room_name = room_info.get('key', room_key)

                    # 创建房间
                    new_room = create_object("typeclasses.rooms.Room", key=room_name)
                    room_objects[room_key] = new_room

                    # 应用房间信息
                    if 'desc' in room_info:
                        new_room.db.desc = room_info['desc']
                    if 'tags' in room_info and isinstance(room_info['tags'], list):
                        for tag in room_info['tags']:
                            new_room.tags.add(tag)
                    if 'attributes' in room_info and isinstance(room_info['attributes'], dict):
                        for key, value in room_info['attributes'].items():
                            # 特殊处理布尔值和数字
                            if isinstance(value, str):
                                if value.lower() == "true":
                                    value = True
                                elif value.lower() == "false":
                                    value = False
                                elif value.isdigit():
                                    value = int(value)
                                elif value.replace('.', '', 1).isdigit():
                                    value = float(value)

                            new_room.attributes.add(key, value)

                    created_rooms[room_key] = room_name
                    self.caller.msg(f"成功创建房间: {room_name}")

                except Exception as e:
                    self.caller.msg(f"创建房间 '{room_key}' 时出错: {e}")
                    import traceback
                    self.caller.msg(f"错误详情: {traceback.format_exc()}")

            # 第二步：设置房间之间的出口连接
            for room_key, room_info in rooms_data.items():
                if room_key in room_objects and 'exits' in room_info:
                    current_room = room_objects[room_key]
                    exits = room_info['exits']

                    for direction, target_room_key in exits.items():
                        if target_room_key in room_objects:
                            target_room = room_objects[target_room_key]
                            # 创建出口
                            exit_obj = create_object(
                                "typeclasses.exits.Exit",
                                key=direction,
                                location=current_room,
                                destination=target_room
                            )
                            self.caller.msg(f"在房间 '{created_rooms[room_key]}' 中创建出口 '{direction}' 指向 '{created_rooms[target_room_key]}'")
                        else:
                            self.caller.msg(f"警告: 在房间 '{created_rooms[room_key]}' 中无法创建指向 '{target_room_key}' 的出口，目标房间不存在")

            self.caller.msg(f"批量创建完成，共创建 {len(created_rooms)} 个房间: {', '.join(created_rooms.values())}")

        except Exception as e:
            self.caller.msg(f"批量创建房间时出错: {e}")
            import traceback
            self.caller.msg(f"错误详情: {traceback.format_exc()}")
