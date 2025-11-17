"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom
from evennia.utils.utils import iter_to_str

from .objects import ObjectParent
from utils.theme_utils import color_room_name


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """
    
    def at_object_creation(self):
        """
        创建房间时初始化室内/室外属性和房间类型
        """
        super().at_object_creation()
        # 默认为室外
        self.db.is_indoor = False
        # 默认房间类型
        self.db.room_type = "normal"
    
    @property
    def is_indoor(self):
        """
        判断房间是否为室内
        
        Returns:
            bool: True表示室内，False表示室外
        """
        return self.db.is_indoor if hasattr(self.db, "is_indoor") else False
    
    @property
    def room_type(self):
        """
        获取房间类型
        
        Returns:
            str: 房间类型，如"normal", "cave", "mountain", "water"等
        """
        return self.db.room_type if hasattr(self.db, "room_type") else "normal"
    
    def set_room_type(self, room_type):
        """
        设置房间类型
        
        Args:
            room_type (str): 房间类型，如"normal", "cave", "mountain", "water"等
        """
        self.db.room_type = room_type.lower()
        
    def get_display_name(self, looker=None, **kwargs):
        """
        获取房间的显示名称，应用主题颜色
        
        Args:
            looker: 查看者对象
            **kwargs: 其他参数
            
        Returns:
            str: 带颜色的房间名
        """
        # 直接使用主题颜色，不使用缓存
            
        # 使用主题颜色
        from server.conf.theme import ROOM_NAME
        return f"{ROOM_NAME}{self.key}|n"
    
    # 自定义外观模板，中文化，确保出口在最下面
    appearance_template = """|c{name}{extra_name_info}|n
{desc}
{header}{characters}{things}{footer}
{exits}"""
    
    def get_display_exits(self, looker, **kwargs):
        """
        重写出口显示，中文化，并添加可点击链接
        """
        def _sort_exit_names(names):
            exit_order = kwargs.get("exit_order")
            if not exit_order:
                return names
            sort_index = {name: key for key, name in enumerate(exit_order)}
            names = sorted(names)
            end_pos = len(sort_index)
            names.sort(key=lambda name: sort_index.get(name, end_pos))
            return names
        
        exits = self.filter_visible(self.contents_get(content_type="exit"), looker, **kwargs)
        exit_names = []
        for exi in exits:
            # 使用lc标签使出口可点击
            exit_names.append(f"|lc{exi.key}|lt{exi.get_display_name(looker, **kwargs)}|le|n")
        exit_names = iter_to_str(_sort_exit_names(exit_names))
        
        if not exit_names:
            return ""
        elif len(exits) == 1:
            return f"这里唯一的出口是: {exit_names}。"
        else:
            return f"这里明显的方向有: {exit_names}。"
    
    def get_display_characters(self, looker, **kwargs):
        """
        重写人物显示，中文化
        """
        characters = self.filter_visible(
            self.contents_get(content_type="character"), looker, **kwargs
        )
        character_names = []
        for char in characters:
            # 获取角色的账号信息
            account = char.account
            # 获取角色的中文名，从account获取first_name和last_name
            if account and hasattr(account, "first_name") and hasattr(account, "last_name"):
                first_name = account.first_name if account.first_name else ""
                last_name = account.last_name if account.last_name else ""
                
                if first_name and last_name:
                    # 有完整的中文名
                    from server.conf.theme import CHARACTER_NAME, ACCOUNT_NAME
                    chinese_name = f"{CHARACTER_NAME}{last_name}{first_name}|n"
                    character_names.append(f"{chinese_name}({ACCOUNT_NAME}{account.key}|n)")
                else:
                    # 没有完整的中文名，使用账号名
                    from server.conf.theme import ACCOUNT_NAME
                    character_names.append(f"{ACCOUNT_NAME}{account.key}|n")
            elif account:
                # 如果没有first_name和last_name属性，使用账号名
                from server.conf.theme import ACCOUNT_NAME
                character_names.append(f"{ACCOUNT_NAME}{account.key}|n")
            else:
                # 如果没有账号，使用默认显示名称
                from server.conf.theme import CHARACTER_NAME
                character_names.append(f"{CHARACTER_NAME}{char.get_display_name(looker, **kwargs)}|n")
        
        character_names = iter_to_str(character_names)
        
        return f"{character_names}" if character_names else ""