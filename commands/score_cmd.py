from evennia import Command

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
        level = caller.db.level if hasattr(caller.db, 'level') else 1
        exp = caller.db.exp if hasattr(caller.db, 'exp') else 0
        exp_needed = caller.db.exp_needed if hasattr(caller.db, 'exp_needed') else 100

        # 生命值
        hp = caller.db.hp if hasattr(caller.db, 'hp') else 100
        max_hp = caller.db.max_hp if hasattr(caller.db, 'max_hp') else 100

        # 法力值
        mana = caller.db.mana if hasattr(caller.db, 'mana') else 100
        max_mana = caller.db.max_mana if hasattr(caller.db, 'max_mana') else 100
        magic_power = caller.db.magic_power if hasattr(caller.db, 'magic_power') else 5

        # 修仙相关属性
        cultivation = caller.db.cultivation if hasattr(caller.db, 'cultivation') else "凡人"
        cultivation_level = caller.db.cultivation_level if hasattr(caller.db, 'cultivation_level') else 0
        spirit_power = caller.db.spirit_power if hasattr(caller.db, 'spirit_power') else 10

        # 基础属性
        strength = caller.db.strength if hasattr(caller.db, 'strength') else 10
        agility = caller.db.agility if hasattr(caller.db, 'agility') else 10
        intelligence = caller.db.intelligence if hasattr(caller.db, 'intelligence') else 10
        constitution = caller.db.constitution if hasattr(caller.db, 'constitution') else 10

        # 金钱
        gold = caller.db.gold if hasattr(caller.db, 'gold') else 0
        silver = caller.db.silver if hasattr(caller.db, 'silver') else 0

        # 显示属性信息
        text = f"""
|c【{caller.key}的状态】|n
|w境界:|n {cultivation} ({cultivation_level})
|w等级:|n {level} |w经验:|n {exp}/{exp_needed}
|w气血:|n |r{hp}|n/|r{max_hp}|n
|w真元:|n |b{mana}|n/|b{max_mana}|n |w法力:|n {magic_power}
|w灵力:|n {spirit_power}

|w根骨:|n {constitution} |w力量:|n {strength}
|w身法:|n {agility} |w悟性:|n {intelligence}

|w金钱:|n {gold}金 {silver}银
"""

        # 如果有已知法术，显示法术信息
        if hasattr(caller.db, 'known_spells') and caller.db.known_spells:
            spells_text = ", ".join(caller.db.known_spells[:3])  # 只显示前3个
            if len(caller.db.known_spells) > 3:
                spells_text += f" 等{len(caller.db.known_spells)}个法术"
            text += f"|w已知法术:|n {spells_text}\n"

        self.msg(text)
