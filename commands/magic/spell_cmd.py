
# 魔法施放命令
from evennia import Command
from evennia.utils import search as default_search
from world.magic.magic_system import get_magic_system

class CmdCast(Command):
    """
    施放一个法术

    用法:
      cast <法术名> [at <目标>]
      cast <法术名> [on <目标>]

    示例:
      cast fireball at goblin
      cast fireball goblin
      cast fireball
    """

    key = "cast"
    aliases = ["施法", "咏唱"]
    locks = "cmd:all()"
    help_category = "魔法"

    def parse(self):
        """解析命令参数"""
        args = self.args.strip()

        # 初始化变量
        self.spell_name = None
        self.target_name = None

        # 检查是否有参数
        if not args:
            return

        # 分离法术名和目标
        # 首先检查是否有 "at" 或 "on" 关键字
        if " at " in args:
            parts = args.split(" at ", 1)
            self.spell_name = parts[0].strip()
            self.target_name = parts[1].strip()
        elif " on " in args:
            parts = args.split(" on ", 1)
            self.spell_name = parts[0].strip()
            self.target_name = parts[1].strip()
        else:
            # 如果没有关键字，尝试按空格分割
            parts = args.split(None, 1)
            self.spell_name = parts[0].strip()
            if len(parts) > 1:
                self.target_name = parts[1].strip()

    def func(self):
        """执行命令"""
        # 检查是否提供了法术名
        if not self.spell_name:
            self.msg("用法: cast <法术名> [at/on <目标>]")
            return

        # 获取魔法系统
        magic_system = get_magic_system()
        if not magic_system:
            self.msg("|r魔法系统未初始化。|n")
            return

        # 检查法术是否存在
        spell = magic_system.get_spell(self.spell_name.lower())
        if not spell:
            self.msg(f"|r未找到法术 '{self.spell_name}'。|n")
            return

        # 检查角色是否有魔法属性
        if not hasattr(self.caller.db, 'mana'):
            self.msg("|r你没有魔法属性，无法施法。|n")
            return

        # 检查角色是否已学会该法术
        if not hasattr(self.caller.db, 'known_spells') or not self.caller.db.known_spells:
            self.msg(f"|r你还没有学会任何法术。|n")
            return
            
        # 尝试直接匹配
        spell_found = False
        if self.spell_name.lower() in self.caller.db.known_spells:
            spell_found = True
        else:
            # 尝试通过魔法系统获取法术，然后匹配中文名称
            magic_system = get_magic_system()
            for spell_key in self.caller.db.known_spells:
                spell = magic_system.get_spell(spell_key)
                if spell and spell.db.name.lower() == self.spell_name.lower():
                    # 更新为实际的法术键值
                    self.spell_name = spell_key
                    spell_found = True
                    break
        
        if not spell_found:
            self.msg(f"|r你还没有学会法术 '{self.spell_name}'。|n")
            return

        # 检查法力值是否足够
        # 确保角色有法力值属性
        if self.caller.db.mana is None:
            self.caller.db.mana = 100  # 默认法力值
            
        if self.caller.db.mana < spell.db.mana_cost:
            self.msg(f"|r你的法力值不足，施放 {spell.db.name} 需要 {spell.db.mana_cost} 点法力。|n")
            return

        # 查找目标
        target = None
        if self.target_name:
            from evennia.utils.search import search_object
            target = search_object(self.target_name)
            if not target:
                self.msg(f"|r找不到目标 '{self.target_name}'。|n")
                return
            target = target[0]

        # 施放法术
        try:
            result = spell.cast(self.caller, target)
            if result:
                self.caller.db.mana -= spell.db.mana_cost  # 扣除法力值
                self.msg(f"|g你成功施放了 {spell.db.name}！|n")
            else:
                self.msg(f"|r施放 {spell.db.name} 失败。|n")
        except Exception as e:
            self.msg(f"|r施放法术时出错: {e}|n")


class CmdSpells(Command):
    """
    查看已学会的法术

    用法:
      spells
    """

    key = "spells"
    aliases = ["法术", "法术列表"]
    locks = "cmd:all()"
    help_category = "魔法"

    def func(self):
        """执行命令"""
        # 获取魔法系统
        magic_system = get_magic_system()
        if not magic_system:
            self.msg("|r魔法系统未初始化。|n")
            return

        # 获取角色已学会的法术
        if not hasattr(self.caller, 'known_spells') or not self.caller.known_spells:
            # 初始化角色的法术列表
            self.caller.db.known_spells = ["fireball"]  # 默认只知道火球术
        
        known_spells = self.caller.db.known_spells

        # 构建输出
        output = "|y你已学会的法术:|n\n"
        for spell_key in known_spells:
            spell = magic_system.get_spell(spell_key)
            if spell:
                output += f"  |c{spell.name}|n - {spell.description} (消耗: {spell.mana_cost}法力)\n"

        self.msg(output)


class CmdSpellInfo(Command):
    """
    查看法术详细信息

    用法:
      spellinfo <法术名>
    """

    key = "spellinfo"
    aliases = ["法术信息", "法术详情"]
    locks = "cmd:all()"
    help_category = "魔法"

    def func(self):
        """执行命令"""
        if not self.args:
            self.msg("用法: spellinfo <法术名>")
            return

        # 获取魔法系统
        magic_system = get_magic_system()
        if not magic_system:
            self.msg("|r魔法系统未初始化。|n")
            return

        # 查找法术
        spell_name = self.args.strip().lower()
        self.msg(f"|g正在查找法术: '{spell_name}'|n")  # 调试信息
        spell = magic_system.get_spell(spell_name)
        if not spell:
            # 尝试通过名称查找
            all_spells = magic_system.get_all_spells()
            for key, s in all_spells.items():
                if s.name.lower() == spell_name:
                    spell = s
                    break
        
        if not spell:
            self.msg(f"|r未找到法术 '{self.args}'。|n")
            return

        # 构建法术信息
        output = f"|y{spell.name}|n\n"
        output += f"|w描述:|n {spell.description}\n"
        output += f"|r元素:|n {spell.element}\n"
        output += f"|w等级:|n {spell.level}\n"
        output += f"|w法力消耗:|n {spell.mana_cost}\n"
        output += f"|w基础伤害:|n {spell.damage}\n"

        self.msg(output)
