
# 为现有角色添加魔法属性的脚本

from evennia import search_account
from typeclasses.characters import Character

def init_magic_for_all_characters():
    """为所有现有角色添加魔法属性"""
    # 获取所有账户
    accounts = search_account("*")

    for account in accounts:
        # 获取账户的所有角色
        characters = account.characters
        for char in characters:
            # 检查是否已有魔法属性
            if not hasattr(char.db, 'mana'):
                print(f"为角色 {char.key} 添加魔法属性...")
                # 添加魔法属性
                char.db.mana = 100
                char.db.max_mana = 100
                char.db.magic_power = 5
                char.db.fire_resistance = 0
                char.db.water_resistance = 0
                char.db.earth_resistance = 0
                char.db.air_resistance = 0
                char.db.lightning_resistance = 0
                char.db.ice_resistance = 0
                char.db.light_resistance = 0
                char.db.dark_resistance = 0

                # 添加已知法术
                char.db.known_spells = ["fireball"]

                # 初始化法术冷却时间
                char.spell_cooldowns = {}

                print(f"角色 {char.key} 的魔法属性已添加")
            else:
                print(f"角色 {char.key} 已有魔法属性，跳过")

if __name__ == "__main__":
    init_magic_for_all_characters()
