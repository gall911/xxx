    def get_xianya_status(self):
        """获取修仙风格的状态信息"""
        # 获取属性配置
        attributes_config = game_config.get_config("basic/attributes")

        # 获取角色属性，使用get方法避免None值
        level = self.db.get('level', 1)
        exp = self.db.get('exp', 0)
        exp_needed = self.db.get('exp_needed', 100)

        # 生命值和法力值
        hp = self.db.get('hp', 100)
        max_hp = self.db.get('max_hp', 100)
        mana = self.db.get('mana', 100)
        max_mana = self.db.get('max_mana', 100)

        # 修仙相关属性
        cultivation = self.db.get('cultivation', "凡人")
        cultivation_level = self.db.get('cultivation_level', 0)
        spirit_power = self.db.get('spirit_power', 10)
        magic_power = self.db.get('magic_power', 5)

        # 基础属性 - 使用配置中的名称
        strength = self.db.get('strength', 10)
        dexterity = self.db.get('dexterity', 10)  # 使用配置中的名称
        intelligence = self.db.get('intelligence', 10)
        constitution = self.db.get('constitution', 10)
        wisdom = self.db.get('wisdom', 10)
        charisma = self.db.get('charisma', 10)
        weapon_proficiency = self.db.get('weapon_proficiency', 10)

        # 金钱
        gold = self.db.get('gold', 0)
        silver = self.db.get('silver', 0)

        # 计算百分比，用于显示进度条
        hp_percent = int(hp / max_hp * 10) if max_hp > 0 else 0
        mana_percent = int(mana / max_mana * 10) if max_mana > 0 else 0
        exp_percent = int(exp / exp_needed * 10) if exp_needed > 0 else 0

        # 创建进度条
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
|c│ |w法力:|n {magic_power} |w灵力:|n {spirit_power}              │|n
|c├────────────────────────────────────────┤|n
|c│ |w体质:|n {constitution} |w力量:|n {strength}                │|n
|c│ |w敏捷:|n {dexterity} |w智力:|n {intelligence}                │|n
|c│ |w智慧:|n {wisdom} |w魅力:|n {charisma}                    │|n
|c│ |w武器熟练:|n {weapon_proficiency}                              │|n
|c├────────────────────────────────────────┤|n
|c│ |w金钱:|n |Y{gold}|n金 |y{silver}|n银                      │|n
|c└────────────────────────────────────────┘|n"""

        # 如果有已知法术，显示法术信息
        known_spells = self.db.get('known_spells', [])
        if known_spells:
            spells_text = ", ".join(known_spells[:3])  # 只显示前3个
            if len(known_spells) > 3:
                spells_text += f" 等{len(known_spells)}个法术"
            text += f"
|c┌────────────────────────────────────────┐|n"
            text += f"|c│ |w已知法术:|n {spells_text}{' ' * (30 - len(spells_text))}│|n"
            text += f"|c└────────────────────────────────────────┘|n"

        return text