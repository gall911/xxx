"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.
"""

from evennia import DefaultExit

# 移除 ObjectParent 继承以防止循环引用
# 如果你确实需要在 ObjectParent 中定义通用的方法，
# 建议将 ObjectParent 移动到一个单独的 mixins.py 文件中，然后从那里导入。
class Exit(DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property and overrides some hooks
    and methods to represent the exits.
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
        # 注意：self.key 可能是多字节字符，lower() 通常没问题，但要注意
        if self.key: 
            key = self.key.lower()
            if key in auto_aliases:
                for alias in auto_aliases[key]:
                    self.aliases.add(alias)