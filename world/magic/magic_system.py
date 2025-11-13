
# 魔法系统核心逻辑
from evennia.scripts.scripts import DefaultScript
from evennia.utils.create import create_object
from world.magic.spells.attack_spells.fire_spells import Fireball

class MagicSystem(DefaultScript):
    """
    魔法系统核心类，负责管理所有法术和施法逻辑
    """
    
    def __init__(self, *args, **kwargs):
        """初始化魔法系统"""
        super().__init__(*args, **kwargs)
        
    def at_script_creation(self):
        """当脚本被创建时调用"""
        super().at_script_creation()
        self.key = "magic_system"
        self.desc = "魔法系统核心脚本"
        self.persistent = True

        # 初始化法术注册表
        self.db.spells = {}
        self.register_default_spells()

    def register_default_spells(self):
        """注册默认法术"""
        # 注册火球术
        try:
            fireball = create_object(Fireball, key="fireball")
            self.register_spell(fireball)
        except Exception as e:
            print(f"创建火球术时出错: {e}")

    def register_spell(self, spell):
        """
        注册一个法术

        Args:
            spell (BaseSpell): 要注册的法术对象
        """
        self.db.spells[spell.key] = spell

    def get_spell(self, spell_key):
        """
        获取指定key的法术

        Args:
            spell_key (str): 法术的key

        Returns:
            BaseSpell or None: 法术对象，如果不存在则返回None
        """
        spell = self.db.spells.get(spell_key, None)
        if spell and hasattr(spell, "id") and spell.id is None:
            # 如果对象没有正确初始化，尝试重新创建
            try:
                new_spell = create_object(type(spell), key=spell_key)
                self.register_spell(new_spell)
                return new_spell
            except Exception as e:
                print(f"重新创建法术时出错: {e}")
                return None
        return spell

    def get_all_spells(self):
        """
        获取所有已注册的法术

        Returns:
            dict: 所有法术的字典 {key: spell}
        """
        return self.db.spells

    def cast_spell(self, caster, spell_key, target=None):
        """
        施放法术

        Args:
            caster (Character): 施法者
            spell_key (str): 法术的key
            target (Character or None): 目标

        Returns:
            tuple: (success, message) - 是否成功及结果消息
        """
        # 获取法术
        spell = self.get_spell(spell_key)
        if not spell:
            return False, f"未找到名为'{spell_key}'的法术。"

        # 检查是否可以施放
        can_cast, reason = spell.can_cast(caster)
        if not can_cast:
            return False, reason

        # 施放法术
        success, message = spell.cast(caster, target)

        # 如果施法成功，设置冷却时间
        if success and hasattr(spell, "db") and hasattr(spell.db, "cooldown") and spell.db.cooldown > 0:
            if not hasattr(caster, 'spell_cooldowns'):
                caster.spell_cooldowns = {}
            caster.spell_cooldowns[spell.db.key] = spell.db.cooldown

        return success, message

# 获取全局魔法系统实例的函数
def get_magic_system():
    """
    获取全局魔法系统实例

    Returns:
        MagicSystem: 魔法系统实例
    """
    from evennia.scripts.models import ScriptDB
    magic_systems = ScriptDB.objects.filter(db_key="magic_system")
    if magic_systems:
        return magic_systems[0]
    else:
        # 如果不存在，创建一个新的
        from evennia import create_script
        magic_system = create_script(MagicSystem, key="magic_system")
        return magic_system
