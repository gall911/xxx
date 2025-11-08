"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from evennia.objects.objects import DefaultExit

from .objects import ObjectParent
from utils.theme_utils import color_exit_name


class Exit(ObjectParent, DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property and overrides some hooks
    and methods to represent the exits.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects child classes like this.

    """
    
    # 方向别名映射
    DIRECTION_ALIASES = {
        "北": ["n", "north"],
        "南": ["s", "south"],
        "东": ["e", "east"],
        "西": ["w", "west"],
        "东北": ["ne", "northeast"],
        "西北": ["nw", "northwest"],
        "东南": ["se", "southeast"],
        "西南": ["sw", "southwest"],
        "上": ["u", "up"],
        "下": ["d", "down"],
        "里": ["in", "inside"],
        "外": ["out", "outside"]
    }
    
    def at_object_creation(self):
        """
        创建出口时设置别名
        """
        super().at_object_creation()
        self._setup_direction_aliases()
    
    def _setup_direction_aliases(self):
        """
        根据出口名称设置方向别名
        """
        key = self.key.lower()
        
        # 检查是否是标准方向
        for direction, aliases in self.DIRECTION_ALIASES.items():
            if key == direction.lower() or key in [a.lower() for a in aliases]:
                # 添加所有别名
                for alias in aliases:
                    if alias not in self.aliases.all():
                        self.aliases.add(alias)
                # 如果当前名称不是中文方向，也添加中文方向
                if key != direction.lower() and direction.lower() not in self.aliases.all():
                    self.aliases.add(direction)
                break
    
    def set_key(self, new_key):
        """
        更改出口名称时重新设置别名
        """
        super().set_key(new_key)
        self._setup_direction_aliases()
        
    def get_display_name(self, looker=None, **kwargs):
        """
        获取出口的显示名称，应用主题颜色
        
        Args:
            looker: 查看者对象
            **kwargs: 其他参数
            
        Returns:
            str: 带颜色的出口名
        """
        # 如果有存储的显示名称，使用它
        if hasattr(self.db, "display_name") and self.db.display_name:
            return self.db.display_name
            
        # 否则使用主题颜色
        return color_exit_name(self.key)
