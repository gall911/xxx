"""开发者命令集"""
from evennia import CmdSet
from evennia import default_cmds
from commands.dev import room_commands, npc_commands, debug_commands
from commands.dev import quick_commands
from commands.dev import test_commands

class DevCmdSet(CmdSet):
    """开发者命令集"""
    
    key = "DevCmdSet"
    priority = 1
    
    def at_cmdset_creation(self):
        """创建命令集"""
        #super().at_cmdset_creation()
        
        # 房间命令
        self.add(room_commands.CmdRoomList())
        self.add(room_commands.CmdRoomAdd())
        self.add(room_commands.CmdRoomBatch())
        self.add(room_commands.CmdRoomConnect())
        
        # NPC命令
        self.add(npc_commands.CmdNPCList())
        self.add(npc_commands.CmdNPCAdd())
        self.add(npc_commands.CmdNPCDelete())
        self.add(npc_commands.CmdNPCBatch())
        # 调试命令
        self.add(debug_commands.CmdDebugGet())
        self.add(debug_commands.CmdDebugSet())
        self.add(debug_commands.CmdDebugReload())
        self.add(debug_commands.CmdDebugData())
        self.add(quick_commands.CmdQuickHeal())
        self.add(quick_commands.CmdQuickInit())
        self.add(debug_commands.CmdAddPassive())
        self.add(test_commands.CmdStressTest())
        self.add(test_commands.CmdIOMonitor())
