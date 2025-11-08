"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom
from evennia.utils.utils import iter_to_str

from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """
    
    # 自定义外观模板，中文化，确保出口在最下面
    appearance_template = """{name}{extra_name_info}
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
            exit_names.append(f"|lc{exi.key}|lt{exi.get_display_name(looker, **kwargs)}|le")
        exit_names = iter_to_str(_sort_exit_names(exit_names))
        
        if not exit_names:
            return ""
        elif len(exits) == 1:
            return f"这里唯一的出口是 {exit_names}。"
        else:
            return f"这里明显的方向有 {exit_names}。"
    
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
            if account and hasattr(account, "first_name") and hasattr(account, "last_name") and account.first_name and account.last_name:
                chinese_name = f"{account.last_name}{account.first_name}"
                character_names.append(f"{chinese_name}({account.key})")
            elif account:
                # 如果没有中文名，使用账号名
                character_names.append(f"{account.key}")
            else:
                # 如果没有账号，使用默认显示名称
                character_names.append(f"{char.get_display_name(looker, **kwargs)}")
        
        character_names = iter_to_str(character_names)
        
        return f"{character_names}" if character_names else ""
