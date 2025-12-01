"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""

from evennia.objects.objects import DefaultExit

from .objects import ObjectParent


class Exit(ObjectParent, DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property and overrides some hooks
    and methods to represent the exits.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects child classes like this.

    """

    pass
"""
Exits

typeclasses/exits.py
"""
from evennia import DefaultExit

class Exit(DefaultExit):
    """
    出口是房间之间的连接器。
    在 Evennia 中，出口本身就是命令。
    """

    def at_object_creation(self):
        """
        当对象第一次被创建时调用。
        """
        super().at_object_creation()

        # === 全局方向别名自动化 ===
        # 只要出口名字匹配（不区分大小写），自动添加简写
        auto_aliases = {
            'north': ['n'],
            'south': ['s'],
            'east':  ['e'],
            'west':  ['w'],
            'up':    ['u'],
            'down':  ['d'],
            'northeast': ['ne'],
            'northwest': ['nw'],
            'southeast': ['se'],
            'southwest': ['sw'],
            'out':   ['o'],
            'enter': ['i']
        }

        # 转换为小写进行匹配
        key = self.key.lower()
        
        if key in auto_aliases:
            for alias in auto_aliases[key]:
                self.aliases.add(alias)

    # 这里的 desc 我们通常保留默认即可，因为我们在 Room.return_appearance 里处理了显示
    # 但如果你想让 'look west' 时有特殊显示，可以在这里写 return_appearance