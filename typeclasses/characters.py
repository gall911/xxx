"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.
"""

from evennia.objects.objects import DefaultCharacter
from evennia import TICKER_HANDLER

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.
    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.
    """

    def at_object_creation(self):
        """
        当角色对象被创建时调用
        """
        super().at_object_creation()

        # 基础属性
        self.db.level = 1  # 等级
        self.db.exp = 0  # 当前经验
        self.db.exp_needed = 100  # 升级所需经验

        # 生命值
        self.db.hp = 100  # 当前生命值
        self.db.max_hp = 100  # 最大生命值

        # 魔法系统相关属性
        self.db.mana = 100  # 当前法力值
        self.db.max_mana = 100  # 最大法力值
        self.db.magic_power = 5  # 魔法强度
        self.db.fire_resistance = 0  # 火系抗性
        self.db.water_resistance = 0  # 水系抗性
        self.db.earth_resistance = 0  # 土系抗性
        self.db.air_resistance = 0  # 风系抗性
        self.db.lightning_resistance = 0  # 雷系抗性
        self.db.ice_resistance = 0  # 冰系抗性
        self.db.light_resistance = 0  # 光系抗性
        self.db.dark_resistance = 0  # 暗系抗性

        # 修仙相关属性
        self.db.cultivation = "凡人"  # 境界
        self.db.cultivation_level = 0  # 境界等级
        self.db.spirit_power = 10  # 灵力

        # 基础属性
        self.db.strength = 10  # 力量
        self.db.agility = 10  # 身法
        self.db.intelligence = 10  # 悟性
        self.db.constitution = 10  # 根骨

        # 金钱
        self.db.gold = 10  # 金币
        self.db.silver = 50  # 银币

        # 已学会的法术列表
        self.db.known_spells = ["fireball"]  # 默认只会火球术

        # 法术冷却时间
        self.spell_cooldowns = {}

        # 启动自动恢复HP和mana的ticker
        TICKER_HANDLER.add(interval=60, callback=self.regen_health_mana, idstring="health_mana_regen")

    def regen_health_mana(self):
        """
        自动恢复HP和mana的方法，由ticker定期调用
        """
        # 确保属性存在
        if not hasattr(self.db, 'hp') or self.db.hp is None:
            self.db.hp = 100
        if not hasattr(self.db, 'max_hp') or self.db.max_hp is None:
            self.db.max_hp = 100
        if not hasattr(self.db, 'mana') or self.db.mana is None:
            self.db.mana = 100
        if not hasattr(self.db, 'max_mana') or self.db.max_mana is None:
            self.db.max_mana = 100

        # 只有在HP和mana低于最大值时才恢复
        hp_regen = False
        mana_regen = False

        # 恢复HP（每分钟恢复最大值的5%）
        if self.db.hp < self.db.max_hp:
            old_hp = self.db.hp
            self.db.hp = min(self.db.max_hp, self.db.hp + int(self.db.max_hp * 0.05))
            if self.db.hp > old_hp:
                hp_regen = True
                self.msg(f"|g你的气血恢复了 {self.db.hp - old_hp} 点。|n")

        # 恢复mana（每分钟恢复最大值的10%）
        if self.db.mana < self.db.max_mana:
            old_mana = self.db.mana
            self.db.mana = min(self.db.max_mana, self.db.mana + int(self.db.max_mana * 0.1))
            if self.db.mana > old_mana:
                mana_regen = True
                self.msg(f"|b你的真元恢复了 {self.db.mana - old_mana} 点。|n")

        return hp_regen or mana_regen

    def at_object_delete(self):
        """
        当角色对象被删除时调用
        """
        # 停止自动恢复HP和mana的ticker
        TICKER_HANDLER.remove(self, "health_mana_regen")
        super().at_object_delete()

    def at_cmdset_get(self, **kwargs):
        """
        当获取命令集时调用，用于添加魔法命令集
        """
        try:
            from commands.magic.magic_cmdset import MagicCmdSet
            self.cmdset.add(MagicCmdSet, persistent=True)
        except Exception as e:
            print(f"添加魔法命令集时出错: {e}")

    # 提供便捷的属性访问
    @property
    def mana(self):
        """获取当前法力值"""
        return self.db.mana

    @mana.setter
    def mana(self, value):
        """设置当前法力值"""
        self.db.mana = max(0, min(value, self.db.max_mana))

    @property
    def max_mana(self):
        """获取最大法力值"""
        return self.db.max_mana

    @max_mana.setter
    def max_mana(self, value):
        """设置最大法力值"""
        self.db.max_mana = max(1, value)

    @property
    def magic_power(self):
        """获取魔法强度"""
        return self.db.magic_power

    @magic_power.setter
    def magic_power(self, value):
        """设置魔法强度"""
        self.db.magic_power = max(0, value)

    @property
    def fire_resistance(self):
        """获取火系抗性"""
        return self.db.fire_resistance

    @fire_resistance.setter
    def fire_resistance(self, value):
        """设置火系抗性"""
        self.db.fire_resistance = max(0, value)

    @property
    def known_spells(self):
        """获取已学会的法术列表"""
        return self.db.known_spells

    @known_spells.setter
    def known_spells(self, value):
        """设置已学会的法术列表"""
        self.db.known_spells = value if isinstance(value, list) else [value]

    def add_spell(self, spell_key):
        """添加一个已学会的法术"""
        if spell_key not in self.db.known_spells:
            self.db.known_spells.append(spell_key)
            return True
        return False

    def remove_spell(self, spell_key):
        """移除一个已学会的法术"""
        if spell_key in self.db.known_spells:
            self.db.known_spells.remove(spell_key)
            return True
        return False

    def get_xianya_status(self):
        """获取修仙风格的状态信息"""
        # 获取角色属性，使用get方法避免None值
        level = self.db.get('level', 1)
        exp = self.db.get('exp', 0)
        exp_needed = self.db.get('exp_needed', 100)

        # 生命值
        hp = self.db.get('hp', 100)
        max_hp = self.db.get('max_hp', 100)

        # 法力值
        mana = self.db.get('mana', 100)
        max_mana = self.db.get('max_mana', 100)
        magic_power = self.db.get('magic_power', 5)

        # 修仙相关属性
        cultivation = self.db.get('cultivation', "凡人")
        cultivation_level = self.db.get('cultivation_level', 0)
        spirit_power = self.db.get('spirit_power', 10)

        # 基础属性
        strength = self.db.get('strength', 10)
        agility = self.db.get('agility', 10)
        intelligence = self.db.get('intelligence', 10)
        constitution = self.db.get('constitution', 10)

        # 金钱
        gold = self.db.get('gold', 0)
        silver = self.db.get('silver', 0)

        # 计算气血和真元的百分比，用于显示进度条
        hp_percent = int(hp / max_hp * 10) if max_hp > 0 else 0
        mana_percent = int(mana / max_mana * 10) if max_mana > 0 else 0
        exp_percent = int(exp / exp_needed * 10) if exp_needed > 0 else 0

        # 创建简单的进度条
        hp_bar = "█" * hp_percent + "░" * (10 - hp_percent)
        mana_bar = "█" * mana_percent + "░" * (10 - mana_percent)
        exp_bar = "█" * exp_percent + "░" * (10 - exp_percent)

        # 构建状态信息文本
        text = f"""
|c┌────────────────────────────────────────┐|n
|c│              |w{self.key}的状态|c              │|n
|c├────────────────────────────────────────┤|n
|c│ |w境界:|n {cultivation} ({cultivation_level})                    │|n
|c│ |w等级:|n {level}                                      │|n
|c│ |w经验:|n |y{exp}|n/|Y{exp_needed}|n {exp_bar}                 │|n
|c├────────────────────────────────────────┤|n
|c│ |w气血:|n |r{hp}|n/|R{max_hp}|n {hp_bar}                 │|n
|c│ |w真元:|n |b{mana}|n/|B{max_mana}|n {mana_bar}                 │|n
|c│ |w法力:|n {magic_power}                              │|n
|c│ |w灵力:|n {spirit_power}                              │|n
|c├────────────────────────────────────────┤|n
|c│ |w根骨:|n {constitution} |w力量:|n {strength}                │|n
|c│ |w身法:|n {agility} |w悟性:|n {intelligence}                │|n
|c├────────────────────────────────────────┤|n
|c│ |w金钱:|n |Y{gold}|n金 |y{silver}|n银                      │|n
|c└────────────────────────────────────────┘|n"""

        # 如果有已知法术，显示法术信息
        known_spells = self.db.get('known_spells', [])
        if known_spells:
            spells_text = ", ".join(self.db.known_spells[:3])  # 只显示前3个
            if len(self.db.known_spells) > 3:
                spells_text += f" 等{len(self.db.known_spells)}个法术"
            text += f"\n|c┌────────────────────────────────────────┐|n"
            text += f"|c│ |w已知法术:|n {spells_text}{' ' * (30 - len(spells_text))}│|n"
            text += f"|c└────────────────────────────────────────┘|n"

        return text
