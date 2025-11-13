
# 魔法命令集
from evennia import CmdSet

try:
    from .spell_cmd import CmdCast, CmdSpells, CmdSpellInfo
    from .magic_admin_cmd import CmdMigrateMagic, CmdReloadMagic, CmdAddSpell, CmdRemoveSpell
    IMPORTS_SUCCESS = True
except ImportError as e:
    print(f"导入魔法命令时出错: {e}")
    IMPORTS_SUCCESS = False

class MagicCmdSet(CmdSet):
    """
    魔法系统命令集，包含所有与魔法相关的命令
    """

    key = "MagicCmdSet"
    priority = 1  # 设置优先级，确保能覆盖默认命令

    def at_cmdset_creation(self):
        """当命令集创建时调用"""
        if not IMPORTS_SUCCESS:
            print("无法添加魔法命令，因为导入失败")
            return
            
        try:
            # 玩家魔法命令
            self.add(CmdCast())
            self.add(CmdSpells())
            self.add(CmdSpellInfo())
            
            # 管理员魔法命令
            self.add(CmdMigrateMagic())
            self.add(CmdReloadMagic())
            self.add(CmdAddSpell())
            self.add(CmdRemoveSpell())
            print("魔法命令集已成功添加")
        except Exception as e:
            print(f"添加魔法命令时出错: {e}")
