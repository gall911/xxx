"""
commands/default_cmdsets.py
核心命令集配置文件 - 稳健防崩版
"""
from evennia import default_cmds

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    所有玩家角色的基础命令集。
    这里的东西，所有人出生就自带。
    """
    key = "Character"

    def at_cmdset_creation(self):
        """
        组装命令集
        """
        # 1. 【核心保险】先加载官方基础命令 (n, s, look, get, inventory...)
        # 只要这行在，基础功能就永远不会丢。
        super().at_cmdset_creation()
        
        # 2. 【开发工具】加载全自动扫描雷达 (DevCmdSet)
        # 使用 try-except 保护，万一开发文件报错，不影响玩家正常游戏
        try:
            from commands.dev.dev_cmdset import DevCmdSet
            self.add(DevCmdSet)
        except Exception as e:
            print(f"|r[警告] 开发命令集加载失败 (不影响基础游戏): {e}|n")

        # 3. 【游戏功能】加载任务系统 (Quest)
        try:
            from commands.quest_commands import (
                CmdQuest, CmdQuestList, CmdAbandon, 
                CmdAcceptQuest, CmdCompleteQuest
            )
            self.add(CmdQuest())
            self.add(CmdQuestList())
            self.add(CmdAbandon())
            self.add(CmdAcceptQuest())
            self.add(CmdCompleteQuest())
        except ImportError:
            # 如果你还没写好 quest_commands.py，这里会静默跳过，不会报错
            pass
        except Exception as e:
            print(f"|r[警告] 任务命令加载失败: {e}|n")

        # 4. 【游戏功能】加载 NPC 交互 (Talk)
        try:
            from commands.npc_commands import CmdTalk, CmdNPCInfo
            self.add(CmdTalk())
            self.add(CmdNPCInfo())
        except ImportError:
            pass
        except Exception as e:
            print(f"|r[警告] NPC命令加载失败: {e}|n")

        
            


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    账号级别的命令 (OOC, 聊天频道等)
    """
    key = "DefaultAccount"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    登录前的命令 (create, connect)
    """
    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    Session 级别的命令 (通常为空)
    """
    key = "DefaultSession"

    def at_cmdset_creation(self):
        super().at_cmdset_creation()