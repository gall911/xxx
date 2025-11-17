
import os
import yaml
from evennia.utils import create
from typeclasses.rooms import Room

class RoomLoader:
    _cache = {}
    _rooms = {}  # 存储已创建的房间对象

    @classmethod
    def _template_path(cls, name):
        return os.path.join(
            os.path.dirname(__file__),
            "rooms",
            f"{name}.yaml"
        )

    @classmethod
    def load(cls, name):
        if name in cls._cache:
            return cls._cache[name]

        path = cls._template_path(name)
        if not os.path.exists(path):
            raise FileNotFoundError(f"Template {name} not found at {path}")

        with open(path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            cls._cache[name] = data
            return data

    @classmethod
    def create_rooms_from_template(cls, template_name="mdl"):
        """
        从YAML模板创建房间

        Args:
            template_name (str): 模板文件名，不包含.yaml后缀

        Returns:
            dict: 创建的房间字典，键为房间ID，值为房间对象
        """
        data = cls.load(template_name)
        rooms_data = data.get('rooms', {})

        # 首先创建所有房间
        for room_id, room_data in rooms_data.items():
            room = create.create_object(
                Room,
                key=room_data.get('key', room_id),
                location=None
            )

            # 设置房间描述
            room.db.desc = room_data.get('desc', '这是一个房间。')

            # 设置房间标签
            if 'tags' in room_data:
                room.tags.add(room_data['tags'])

            # 设置房间属性
            if 'attributes' in room_data:
                for attr_name, attr_value in room_data['attributes'].items():
                    setattr(room.db, attr_name, attr_value)

            # 保存到房间字典
            cls._rooms[room_id] = room

        # 然后设置房间之间的出口
        for room_id, room_data in rooms_data.items():
            room = cls._rooms[room_id]
            exits_data = room_data.get('exits', {})

            for direction, target_id in exits_data.items():
                if target_id in cls._rooms:
                    target_room = cls._rooms[target_id]
                    # 创建出口
                    create.create_object(
                        "typeclasses.exits.Exit",
                        key=direction,
                        location=room,
                        destination=target_room
                    )

        return cls._rooms

    @classmethod
    def get_room(cls, room_id):
        """
        获取已创建的房间对象

        Args:
            room_id (str): 房间ID

        Returns:
            Room: 房间对象，如果不存在则返回None
        """
        return cls._rooms.get(room_id)

    @classmethod
    def clear_cache(cls):
        """
        清除所有缓存
        """
        cls._cache.clear()
