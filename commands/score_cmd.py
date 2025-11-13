from evennia import Command
from utils.config_manager import game_config

class CmdScore(Command):
    """
    查看角色属性信息

    用法:
      score
      sc

    显示你的角色当前状态，包括等级、经验、生命值、法力值等属性。
    """

    key = "score"
    aliases = ["sc", "属性", "状态"]
    locks = "cmd:all()"
    help_category = "通用"

    def func(self):
        """执行命令"""
        caller = self.caller

        # 获取角色属性
        level = getattr(caller.db, 'level', 1)
        exp = getattr(caller.db, 'exp', 0)
        exp_needed = getattr(caller.db, 'exp_needed', 100)

        # 生命值
        hp = getattr(caller.db, 'hp', 100)
        max_hp = getattr(caller.db, 'max_hp', 100)

        # 法力值
        mana = getattr(caller.db, 'mana', 100)
        max_mana = getattr(caller.db, 'max_mana', 100)
        magic_power = getattr(caller.db, 'magic_power', 5)

        # 修仙相关属性
        cultivation_key = getattr(caller.db, 'cultivation', "凡人")
        cultivation_level = getattr(caller.db, 'cultivation_level', 0)
        spirit_power = getattr(caller.db, 'spirit_power', 10)

        # 从配置中获取境界名称
        realms_config = game_config.get_config("basic/realms")
        if realms_config and "realms" in realms_config and cultivation_key in realms_config["realms"]:
            cultivation = realms_config["realms"][cultivation_key].get("name", cultivation_key)
        else:
            cultivation = cultivation_key

        # 从配置中获取属性名称
        attributes_config = game_config.get_config("basic/attributes")
        def get_attr_name(attr_key):
            """从配置中获取属性名称"""
            if attributes_config and "attributes" in attributes_config and attr_key in attributes_config["attributes"]:
                return attributes_config["attributes"][attr_key].get("name", attr_key)
            return attr_key

        # 基础属性 - 使用配置中的名称
        strength = getattr(caller.db, 'strength', 10)
        dexterity = getattr(caller.db, 'dexterity', 10)
        intelligence = getattr(caller.db, 'intelligence', 10)
        constitution = getattr(caller.db, 'constitution', 10)
        wisdom = getattr(caller.db, 'wisdom', 10)
        charisma = getattr(caller.db, 'charisma', 10)

        # 金钱
        gold = getattr(caller.db, 'gold', 0)
        silver = getattr(caller.db, 'silver', 0)

        # 获取属性名称
        constitution_name = get_attr_name("constitution")
        strength_name = get_attr_name("strength")
        dexterity_name = get_attr_name("dexterity")
        intelligence_name = get_attr_name("intelligence")

        # 显示属性信息
        text = f"""
|c【{caller.key}的状态】|n
|w境界:|n {cultivation} ({cultivation_level})
|w等级:|n {level} |w经验:|n {exp}/{exp_needed}
|w气血:|n |r{hp}|n/|r{max_hp}|n
|w真元:|n |b{mana}|n/|b{max_mana}|n |w法力:|n {magic_power}
|w灵力:|n {spirit_power}

|w{constitution_name}:|n {constitution} |w{strength_name}:|n {strength}
|w{dexterity_name}:|n {dexterity} |w{intelligence_name}:|n {intelligence}

|w金钱:|n {gold}金 {silver}银"""

        # 如果有已知法术，显示法术信息
        known_spells = getattr(caller.db, 'known_spells', [])
        if known_spells:
            spells_text = ", ".join(known_spells[:3])  # 只显示前3个
            if len(known_spells) > 3:
                spells_text += f" 等{len(known_spells)}个法术"
            text += f"\n|w已知法术:|n {spells_text}"

        self.msg(text)