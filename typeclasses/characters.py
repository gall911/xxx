"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.
"""

from evennia.objects.objects import DefaultCharacter
from evennia import TICKER_HANDLER
from evennia import CmdSet
from commands.hp_cmd import CmdHp
from .objects import ObjectParent
from utils.config_manager import game_config


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

        # 获取角色属性配置
        attributes_config = game_config.get_config("basic/attributes")
        realms_config = game_config.get_config("basic/realms")
        
        # 初始化基础属性
        self.db.level = 1  # 等级
        self.db.exp = 0  # 当前经验
        self.db.exp_needed = realms_config["experience_per_level"]  # 升级所需经验

        # 初始化角色基础属性
        for attr_name, attr_data in attributes_config["attributes"].items():
            # 使用配置中的默认值
            setattr(self.db, attr_name, attr_data["default_value"])
        
        # 计算衍生属性
        self._calculate_derived_attributes()

        # 修仙相关属性
        self.db.cultivation = realms_config["starting_realm"]  # 境界
        self.db.cultivation_level = 0  # 境界等级
        self.db.spirit_power = realms_config["starting_spirit_power"]  # 灵力

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
        # 获取属性配置
        attributes_config = game_config.get_config("basic/attributes")
        
        # 确保属性存在
        if not hasattr(self.db, 'hp') or self.db.hp is None:
            self.db.hp = attributes_config["formulas"]["health"]["base"]
        if not hasattr(self.db, 'max_hp') or self.db.max_hp is None:
            self.db.max_hp = attributes_config["formulas"]["health"]["base"]
        if not hasattr(self.db, 'mana') or self.db.mana is None:
            self.db.mana = attributes_config["formulas"]["mana"]["base"]
        if not hasattr(self.db, 'max_mana') or self.db.max_mana is None:
            self.db.max_mana = attributes_config["formulas"]["mana"]["base"]

        # 只有在HP和mana低于最大值时才恢复
        hp_regen = False
        mana_regen = False

        # 恢复HP（每分钟恢复最大值的5%）
        if self.db.hp < self.db.max_hp:
            old_hp = self.db.hp
            hp_recovery_rate = attributes_config.get("recovery_rates", {}).get("hp_recovery_rate", 0.05)
            self.db.hp = min(self.db.max_hp, self.db.hp + int(self.db.max_hp * hp_recovery_rate))
            if self.db.hp > old_hp:
                hp_regen = True
                self.msg(f"|g你的气血恢复了 {self.db.hp - old_hp} 点。|n")

        # 恢复mana（每分钟恢复最大值的10%）
        if self.db.mana < self.db.max_mana:
            old_mana = self.db.mana
            mana_recovery_rate = attributes_config.get("recovery_rates", {}).get("mana_recovery_rate", 0.1)
            self.db.mana = min(self.db.max_mana, self.db.mana + int(self.db.max_mana * mana_recovery_rate))
            if self.db.mana > old_mana:
                mana_regen = True
                self.msg(f"|b你的真元恢复了 {self.db.mana - old_mana} 点。|n")

        return hp_regen or mana_regen

    def _calculate_derived_attributes(self):
        """
        计算衍生属性
        """
        import math
        
        # 获取属性配置
        attributes_config = game_config.get_config("basic/attributes")
        
        # 准备计算环境
        env = {
            "level": self.db.level,
            "min": min,
            "max": max,
            "int": int,
            "float": float,
            "round": round,
            "math": math,
        }
        
        # 添加所有基础属性到环境
        for attr_name in attributes_config["attributes"]:
            if hasattr(self.db, attr_name):
                env[attr_name] = getattr(self.db, attr_name)
        
        # 计算衍生属性
        for attr_name, formula_data in attributes_config["formulas"].items():
            # 获取基础值
            base_value = formula_data["base"]
            env["base"] = base_value
            
            # 计算属性值
            try:
                value = eval(formula_data["formula"], {"__builtins__": {}}, env)
                setattr(self.db, attr_name, value)
                
                # 设置最大值
                if attr_name == "health":
                    self.db.hp = self.db.max_hp = int(value)
                elif attr_name == "mana":
                    self.db.mana = self.db.max_mana = int(value)
            except Exception as e:
                print(f"计算属性 {attr_name} 失败: {e}")
                setattr(self.db, attr_name, base_value)
    
    def level_up(self):
        """
        角色升级
        """
        # 获取属性配置
        attributes_config = game_config.get_config("basic/attributes")
        realms_config = game_config.get_config("basic/realms")
        
        # 增加等级
        self.db.level += 1
        
        # 重置经验
        self.db.exp = 0
        self.db.exp_needed = realms_config["experience_per_level"] * self.db.level
        
        # 获取主属性和副属性（如果有职业系统）
        # 这里暂时使用默认的成长率
        for attr_name, attr_data in attributes_config["attributes"].items():
            growth_rate = attr_data["growth_rate"]
            
            # 增加属性值
            increase = int(growth_rate)
            if (growth_rate % 1) >= 0.5:
                increase += 1
            
            current_value = getattr(self.db, attr_name)
            new_value = min(
                attr_data["max_value"], 
                current_value + increase
            )
            setattr(self.db, attr_name, new_value)
        
        # 重新计算衍生属性
        self._calculate_derived_attributes()
        
        # 检查是否可以突破境界
        realm_data = realms_config["realms"].get(self.db.cultivation, {})
        if realm_data and self.db.level >= realm_data.get("level_requirement", float("inf")):
            self.msg(f"你的等级已经达到了突破到下一境界的条件！")
    
    def breakthrough_realm(self):
        """
        突破境界
        """
        # 获取境界配置
        realms_config = game_config.get_config("basic/realms")
        
        # 获取当前境界信息
        current_realm = realms_config["realms"].get(self.db.cultivation, {})
        if not current_realm:
            self.msg("无法获取当前境界信息！")
            return False
        
        # 获取下一境界名称
        next_realm_name = current_realm.get("next_realm")
        if not next_realm_name:
            self.msg("你已经达到了最高境界！")
            return False
        
        # 获取下一境界信息
        next_realm = realms_config["realms"].get(next_realm_name)
        if not next_realm:
            self.msg("无法获取下一境界信息！")
            return False
        
        # 检查等级是否满足要求
        if self.db.level < next_realm.get("level_requirement", float("inf")):
            self.msg(f"突破到{next_realm['name']}需要等级达到{next_realm['level_requirement']}级！")
            return False
        
        # 检查突破条件
        breakthrough_conditions = realms_config["realm_breakthrough"].get(next_realm_name, {})
        
        # 检查金币
        gold_cost = breakthrough_conditions.get("gold_cost", 0)
        if self.db.gold < gold_cost:
            self.msg(f"突破到{next_realm['name']}需要{gold_cost}金币！")
            return False
        
        # 检查物品（这里简化处理，实际应该检查背包）
        required_items = breakthrough_conditions.get("items", [])
        # TODO: 实现物品检查
        
        # 扣除金币
        self.db.gold -= gold_cost
        
        # 提升境界
        old_realm = self.db.cultivation
        self.db.cultivation = next_realm_name
        self.db.cultivation_level += 1
        
        # 应用境界加成
        # 增加灵力
        spirit_bonus = next_realm.get("spirit_power_bonus", 0)
        self.db.spirit_power += spirit_bonus
        
        # 增加属性
        attributes_bonus = next_realm.get("attributes_bonus", {})
        for attr_name, bonus in attributes_bonus.items():
            current_value = getattr(self.db, attr_name, 0)
            setattr(self.db, attr_name, current_value + bonus)
        
        # 重新计算衍生属性
        self._calculate_derived_attributes()
        
        # 发送成功消息
        self.msg(f"|g恭喜你成功突破到{next_realm['name']}！|n")
        self.msg(f"|y你的灵力增加了{spirit_bonus}点！|n")
        
        # 显示属性加成
        if attributes_bonus:
            bonus_text = ", ".join([f"{attr}+{value}" for attr, value in attributes_bonus.items()])
            self.msg(f"|y你的属性加成：{bonus_text}|n")
        
        # 通知周围玩家
        self.location.msg_contents(f"|c{self.key}突破到了{next_realm['name']}！|n", exclude=[self])
        
        return True
    
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
        # 获取属性配置
        attributes_config = game_config.get_config("basic/attributes")
        
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

        # 基础属性 - 使用配置中的名称
        strength = self.db.get('strength', 10)
        agility = self.db.get('dexterity', 10)  # 使用配置中的名称
        intelligence = self.db.get('intelligence', 10)
        constitution = self.db.get('constitution', 10)
        weapon_proficiency = self.db.get('weapon_proficiency', 10)

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

       