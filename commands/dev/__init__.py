"""
commands/dev 开发者命令包
"""

# 1. 将各个子模块暴露出来
# 这样你可以直接用 import commands.dev.npc_commands 或 from commands.dev import npc_commands
from . import debug_commands
from . import npc_commands
from . import quick_commands
from . import room_commands
from . import test_commands
from .test_quest_cmd import CmdTestQuest
from .builder_command import CmdSpawnNPC, CmdQuickNPC, CmdSpawnRoom, CmdListData, CmdShowData


# 2. 将核心的 CmdSet 直接暴露在顶层
# 这样在 settings.py 里就可以直接写: from commands.dev import DevCmdSet
from .dev_cmdset import DevCmdSet

# 3. (可选) 如果你希望可以直接 import CmdNPCList
# from .npc_commands import CmdNPCList, CmdNPCAdd, CmdNPCDelete
# from .room_commands import CmdRoomList, CmdRoomAdd
# ... 这种写法会让 __init__.py 变得很长，通常建议只暴露模块(上面第1步)