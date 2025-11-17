"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""
# from commands.character_cmd import CmdCharacter  # 已删除
from evennia import default_cmds
from evennia import Command




class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        # 先调用父类方法，加载所有默认命令（包括 look、l 等）
        super().at_cmdset_creation()
        
        # 验证默认命令是否存在
        look_cmd = None
        for cmd in self.commands:
            if hasattr(cmd, 'key') and cmd.key == 'look':
                look_cmd = cmd
                break
        
        #
        # any commands you add below will overload the default ones.
        #
        # 添加xx命令
        try:
            from commands.mycmd.xx.xx import CmdXX
            self.add(CmdXX)
        except Exception as e:
            import traceback
            import sys
            print(f"Warning: Could not add xx command to command set: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
        
        # 再次验证 look 命令是否还在
        look_after = None
        for cmd in self.commands:
            if hasattr(cmd, 'key') and cmd.key == 'look':
                look_after = cmd
                break
        
        # 如果 look 命令消失了，尝试重新添加
        if look_cmd and not look_after:
            import sys
            print("ERROR: look command was removed! Attempting to restore...", file=sys.stderr)
            # 重新添加 look 命令
            from evennia import default_cmds
            self.add(default_cmds.CmdLook)
        
        # 添加系统命令集
        try:
            from commands.syscmdset import SysCmdSet
            self.add(SysCmdSet)
        except Exception as e:
            import traceback
            import sys
            print(f"Warning: Could not add sys command set: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            
        # 添加仙侠移动命令集
        try:
            from commands.xianyamovecmdset import XianyaMoveCmdSet
            self.add(XianyaMoveCmdSet)
        except Exception as e:
            import traceback
            import sys
            print(f"Warning: Could not add xianya move command set: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            
        # 添加技能系统命令集
        try:
            from commands.skill_cmdset import SkillCmdSet
            self.add(SkillCmdSet)
        except Exception as e:
            import traceback
            import sys
            print(f"Warning: Could not add skill command set: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            
        # 添加自定义add命令
        try:
            from commands.mycmd.add_cmd_new import CmdAdd
            self.add(CmdAdd)
        except Exception as e:
            import traceback
            import sys
            print(f"Warning: Could not add add command: {e}", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            
        


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
        # 添加角色设定命令 - 已删除
        # self.add(CmdCharacter())


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #