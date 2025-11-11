"""
File-based help entries. These complements command-based help and help entries
added in the database using the `sethelp` command in-game.

Control where Evennia reads these entries with `settings.FILE_HELP_ENTRY_MODULES`,
which is a list of python-paths to modules to read.

A module like this should hold a global `HELP_ENTRY_DICTS` list, containing
dicts that each represent a help entry. If no `HELP_ENTRY_DICTS` variable is
given, all top-level variables that are dicts in the module are read as help
entries.

Each dict is on the form
::

    {'key': <str>,
     'text': <str>}``     # the actual help text. Can contain # subtopic sections
     'category': <str>,   # optional, otherwise settings.DEFAULT_HELP_CATEGORY
     'aliases': <list>,   # optional
     'locks': <str>       # optional, 'view' controls seeing in help index, 'read'
                          #           if the entry can be read. If 'view' is unset,
                          #           'read' is used for the index. If unset, everyone
                          #           can read/view the entry.

"""

HELP_ENTRY_DICTS = [
    {
        "key": "evennia",
        "aliases": ["ev"],
        "category": "General",
        "locks": "read:perm(Developer)",
        "text": """
            Evennia is a MU-game server and framework written in Python. You can read more
            on https://www.evennia.com.

            # subtopics

            ## Installation

            You'll find installation instructions on https://www.evennia.com.

            ## Community

            There are many ways to get help and communicate with other devs!

            ### Discussions

            The Discussions forum is found at https://github.com/evennia/evennia/discussions.

            ### Discord

            There is also a discord channel for chatting - connect using the
            following link: https://discord.gg/AJJpcRUhtF

        """,
    },
     {
        "key": "theme",
        "category": "Admin",
        "text": """
主题系统帮助

主题系统允许自定义游戏中各种文本的显示颜色。以下是可用的颜色类型：

基础颜色：
- CHARACTER_NAME: 角色名颜色
- ACCOUNT_NAME: 账号名颜色
- ROOM_NAME: 房间名颜色
- EXIT_NAME: 出口名颜色
- SYSTEM_MSG: 系统消息颜色
- SUCCESS_MSG: 成功消息颜色
- ERROR_MSG: 错误消息颜色

使用方法：
1. 在代码中直接使用颜色常量：
   from server.conf.theme import CHARACTER_NAME
   colored_name = f"{CHARACTER_NAME}{name}|n"

2. 使用工具函数：
   from utils.theme_utils import color_character_name
   colored_name = color_character_name(name)

注意事项：
- 所有颜色标记后需要添加|n来重置格式
- 颜色代码使用|符号开头，后跟颜色标识符
""",
    },
]
