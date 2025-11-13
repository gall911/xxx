
# 魔法系统管理员命令
from evennia import Command
from evennia.utils import search as default_search
from world.magic.migrate_characters import migrate_characters, migrate_single_character

class CmdMigrateMagic(Command):
    """
    为角色添加魔法系统属性

    用法:
      migratemagic [角色名]
      magicmigrate [角色名]

    如果不指定角色名，将为所有角色添加魔法属性。
    如果指定角色名，将只为该角色添加魔法属性。

    示例:
      migratemagic - 为所有角色添加魔法属性
      migratemagic Tom - 只为Tom添加魔法属性
      magicmigrate Jerry - 只为Jerry添加魔法属性
    """

    key = "migratemagic"
    aliases = ["magicmigrate", "mm", "addmagic"]
    locks = "cmd:perm(admins)"
    help_category = "魔法"

    def func(self):
        """执行命令"""
        if not self.args:
            # 迁移所有角色
            result = migrate_characters()
            self.msg(f"|g{result}|n")
        else:
            # 迁移指定角色
            from evennia import search_object
            # 去除参数中的空格
            char_name = self.args.strip()

            # 添加调试信息
            self.msg(f"正在搜索角色: '{char_name}'")

            # 使用简单的搜索方法
            try:
                # 直接使用Evennia的标准搜索功能
                target = search_object(char_name)
                self.msg(f"精确搜索找到 {len(target) if target else 0} 个结果")

                # 如果没找到，尝试使用通配符搜索
                if not target:
                    target = search_object(f"*{char_name}*")
                    self.msg(f"模糊搜索找到 {len(target) if target else 0} 个结果")

                if not target:
                    # 最后尝试：搜索所有对象
                    all_objects = search_object("*")
                    self.msg(f"总共有 {len(all_objects)} 个对象")
                    for obj in all_objects[:5]:  # 只显示前5个
                        self.msg(f"  - {obj.key} (类型: {type(obj).__name__})")

                    self.msg(f"找不到角色'{char_name}'。")
                    return
            except Exception as e:
                self.msg(f"搜索角色时出错: {e}")
                return

            char = target[0]
            # 使用migrate_single_character函数来添加所有属性
            result = migrate_single_character(char)
            self.msg(f"|g{result}|n")


class CmdReloadMagic(Command):
    """
    重新加载魔法系统

    用法:
      reloadmagic

    此命令将重新初始化魔法系统，重新注册所有法术。
    """

    key = "reloadmagic"
    locks = "cmd:perm(admins)"
    help_category = "魔法"

    def func(self):
        """执行命令"""
        from world.magic import init_magic_system

        try:
            magic_system = init_magic_system()
            self.msg("|g魔法系统已成功重新加载。|n")
        except Exception as e:
            self.msg(f"|r重新加载魔法系统时出错: {e}|n")


class CmdAddSpell(Command):
    """
    给角色添加一个法术

    用法:
      addspell <角色名> = <法术名>

    示例:
      addspell Tom = fireball
    """

    key = "addspell"
    locks = "cmd:perm(admins)"
    help_category = "魔法"

    def parse(self):
        """解析命令参数"""
        if not self.args or "=" not in self.args:
            self.target_name = None
            self.spell_name = None
            return

        target, spell = self.args.split("=", 1)
        self.target_name = target.strip()
        self.spell_name = spell.strip().lower()

    def func(self):
        """执行命令"""
        if not self.target_name or not self.spell_name:
            self.msg("用法: addspell <角色名> = <法术名>")
            return

        # 查找目标角色
        target = default_search.object_search(self.target_name, caller=self.caller)
        if not target:
            self.msg(f"找不到角色'{self.target_name}'。")
            return

        char = target[0]

        # 确保角色有魔法属性
        if not hasattr(char.db, 'mana'):
            migrate_single_character(char)

        # 添加法术
        if char.add_spell(self.spell_name):
            self.msg(f"|g成功为{char.key}添加了法术'{self.spell_name}'。|n")
            if char.sessions.count():
                char.msg(f"|y你学会了新法术: {self.spell_name}|n")
        else:
            self.msg(f"|r{char.key}已经知道法术'{self.spell_name}'了。|n")


class CmdRemoveSpell(Command):
    """
    从角色移除一个法术

    用法:
      removespell <角色名> = <法术名>

    示例:
      removespell Tom = fireball
    """

    key = "removespell"
    locks = "cmd:perm(admins)"
    help_category = "魔法"

    def parse(self):
        """解析命令参数"""
        if not self.args or "=" not in self.args:
            self.target_name = None
            self.spell_name = None
            return

        target, spell = self.args.split("=", 1)
        self.target_name = target.strip()
        self.spell_name = spell.strip().lower()

    def func(self):
        """执行命令"""
        if not self.target_name or not self.spell_name:
            self.msg("用法: removespell <角色名> = <法术名>")
            return

        # 查找目标角色
        target = default_search.object_search(self.target_name, caller=self.caller)
        if not target:
            self.msg(f"找不到角色'{self.target_name}'。")
            return

        char = target[0]

        # 确保角色有魔法属性
        if not hasattr(char.db, 'mana'):
            self.msg(f"|r{char.key}没有魔法系统属性。|n")
            return

        # 移除法术
        if char.remove_spell(self.spell_name):
            self.msg(f"|g成功从{char.key}移除了法术'{self.spell_name}'。|n")
            if char.sessions.count():
                char.msg(f"|y你忘记了法术: {self.spell_name}|n")
        else:
            self.msg(f"|r{char.key}不知道法术'{self.spell_name}'。|n")
