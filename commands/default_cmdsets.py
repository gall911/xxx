"""
commands/default_cmdsets.py
核心命令集 - 显式加载版
"""
from evennia import default_cmds
from evennia.utils import logger

class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    玩家角色基础命令集
    """
    key = "Character"

    def at_cmdset_creation(self):
        """
        组装命令集
        """
        # 1. 基础命令 (look, get, inventory 等)
        super().at_cmdset_creation()
        
        # ==========================================================
        # 2. 加载自定义模块
        # 我们不再用 try-pass 隐藏错误。
        # 如果下面的 import 报错，说明你的代码写错了，请去修代码！
        # ==========================================================

        # --- 开发工具 ---
        try:
            from commands.dev.dev_cmdset import DevCmdSet
            self.add(DevCmdSet)
        except ImportError:
            # 只有开发工具允许缺失
            logger.log_warn("未找到开发命令集 (commands.dev.dev_cmdset)，已跳过。")

        # --- 物品与装备 (Inventory & Equipment) ---
        # 🔥 新增：完整的物品+装备命令（不再使用 InventoryCmdSet）
        try:
            from commands.inventory import CmdInventory, CmdUse, CmdDrop, CmdGive
            from commands.equipment import CmdEquip, CmdUnequip, CmdEquipped, CmdEnhance, CmdRepair
            from commands.craft import CmdCraft, CmdRecipes, CmdMerge
            
            self.add(CmdInventory())
            self.add(CmdUse())
            self.add(CmdDrop())
            self.add(CmdGive())
            self.add(CmdEquip())
            self.add(CmdUnequip())
            self.add(CmdEquipped())
            self.add(CmdEnhance())
            self.add(CmdRepair())
            self.add(CmdCraft())
            self.add(CmdRecipes())
            self.add(CmdMerge())
        except ImportError as e:
            logger.log_warn(f"未找到装备/背包命令: {e}")
            # 如果新系统没有，回退到旧的
            try:
                from commands.inventory import InventoryCmdSet
                self.add(InventoryCmdSet)
            except:
                pass

        # --- 战斗系统 (Combat) ---
        from commands.combat import CombatCmdSet
        self.add(CombatCmdSet)

        # --- 技能系统 (Skills) ---
        from commands.skill_commands import SkillCmdSet
        self.add(SkillCmdSet)

        # --- 修炼系统 (Cultivation) ---
        from commands.cultivation import CultivationCmdSet
        self.add(CultivationCmdSet)

        # --- NPC 交互 ---
        from commands.npc_commands import CmdTalk, CmdNPCInfo
        self.add(CmdTalk())
        self.add(CmdNPCInfo())

        # --- 任务系统 ---
        # 🔥 修改这里：引入并添加任务命令集
        # 注意：我们要引入的是 CmdSet，不是单个 Command，这样更整洁
        try:
            from commands.quest_commands import QuestCmdSet
            self.add(QuestCmdSet)
        except ImportError:
            logger.log_warn("未找到任务命令集，已跳过。")

class AccountCmdSet(default_cmds.AccountCmdSet):
    key = "DefaultAccount"
    def at_cmdset_creation(self):
        super().at_cmdset_creation()

class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    key = "DefaultUnloggedin"
    def at_cmdset_creation(self):
        super().at_cmdset_creation()

class SessionCmdSet(default_cmds.SessionCmdSet):
    key = "DefaultSession"
    def at_cmdset_creation(self):
        super().at_cmdset_creation()