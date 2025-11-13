
# 角色迁移脚本 - 为已有角色添加魔法系统属性

def migrate_characters():
    """
    为所有已有角色添加魔法系统相关属性
    """
    from evennia import search_object

    # 查找所有角色对象
    # 使用更精确的搜索方式，确保只获取角色对象
    all_characters = [obj for obj in search_object("*") if hasattr(obj, 'account')]

    migrated_count = 0

    for char in all_characters:
        # 检查角色是否已经有基本属性
        needs_migration = False

        # 检查并添加基础属性
        if not hasattr(char.db, 'level') or char.db.level is None:
            char.db.level = 1
            needs_migration = True
        if not hasattr(char.db, 'exp') or char.db.exp is None:
            char.db.exp = 0
            needs_migration = True
        if not hasattr(char.db, 'exp_needed') or char.db.exp_needed is None:
            char.db.exp_needed = 100
            needs_migration = True

        # 生命值
        if not hasattr(char.db, 'hp') or char.db.hp is None:
            char.db.hp = 100
            needs_migration = True
        if not hasattr(char.db, 'max_hp') or char.db.max_hp is None:
            char.db.max_hp = 100
            needs_migration = True

        # 检查角色是否已经有魔法属性
        if not hasattr(char.db, 'mana') or char.db.mana is None:
            # 添加魔法系统相关属性
            char.db.mana = 100  # 当前法力值
            char.db.max_mana = 100  # 最大法力值
            char.db.magic_power = 5  # 魔法强度
            char.db.fire_resistance = 0  # 火系抗性
            char.db.water_resistance = 0  # 水系抗性
            char.db.earth_resistance = 0  # 土系抗性
            char.db.air_resistance = 0  # 风系抗性
            char.db.lightning_resistance = 0  # 雷系抗性
            char.db.ice_resistance = 0  # 冰系抗性
            char.db.light_resistance = 0  # 光系抗性
            char.db.dark_resistance = 0  # 暗系抗性
            needs_migration = True

        # 修仙相关属性
        if not hasattr(char.db, 'cultivation') or char.db.cultivation is None:
            char.db.cultivation = "凡人"  # 境界
            needs_migration = True
        if not hasattr(char.db, 'cultivation_level') or char.db.cultivation_level is None:
            char.db.cultivation_level = 0  # 境界等级
            needs_migration = True
        if not hasattr(char.db, 'spirit_power') or char.db.spirit_power is None:
            char.db.spirit_power = 10  # 灵力
            needs_migration = True

        # 基础属性
        if not hasattr(char.db, 'strength') or char.db.strength is None:
            char.db.strength = 10  # 力量
            needs_migration = True
        if not hasattr(char.db, 'agility') or char.db.agility is None:
            char.db.agility = 10  # 身法
            needs_migration = True
        if not hasattr(char.db, 'intelligence') or char.db.intelligence is None:
            char.db.intelligence = 10  # 悟性
            needs_migration = True
        if not hasattr(char.db, 'constitution') or char.db.constitution is None:
            char.db.constitution = 10  # 根骨
            needs_migration = True

        # 金钱
        if not hasattr(char.db, 'gold') or char.db.gold is None:
            char.db.gold = 10  # 金币
            needs_migration = True
        if not hasattr(char.db, 'silver') or char.db.silver is None:
            char.db.silver = 50  # 银币
            needs_migration = True

        # 已学会的法术列表
        if not hasattr(char.db, 'known_spells') or char.db.known_spells is None:
            char.db.known_spells = ["fireball"]  # 默认只会火球术
            needs_migration = True

        # 法术冷却时间
        if not hasattr(char, 'spell_cooldowns'):
            char.spell_cooldowns = {}
            needs_migration = True

        if needs_migration:
            migrated_count += 1

            # 通知角色（如果在线）
            if char.sessions.count():
                char.msg("|y你的角色已更新，现在可以使用魔法系统了！|n")

    return f"迁移完成，共更新了 {migrated_count} 个角色。"

def migrate_single_character(char):
    """
    为单个角色添加魔法系统相关属性

    Args:
        char: 要迁移的角色对象

    Returns:
        str: 迁移结果消息
    """
    needs_migration = False

    # 检查并添加基础属性
    if not hasattr(char.db, 'level') or char.db.level is None:
        char.db.level = 1
        needs_migration = True
    if not hasattr(char.db, 'exp') or char.db.exp is None:
        char.db.exp = 0
        needs_migration = True
    if not hasattr(char.db, 'exp_needed') or char.db.exp_needed is None:
        char.db.exp_needed = 100
        needs_migration = True

    # 生命值
    if not hasattr(char.db, 'hp') or char.db.hp is None:
        char.db.hp = 100
        needs_migration = True
    if not hasattr(char.db, 'max_hp') or char.db.max_hp is None:
        char.db.max_hp = 100
        needs_migration = True

    # 检查角色是否已经有魔法属性
    if not hasattr(char.db, 'mana') or char.db.mana is None:
        # 添加魔法系统相关属性
        char.db.mana = 100  # 当前法力值
        char.db.max_mana = 100  # 最大法力值
        char.db.magic_power = 5  # 魔法强度
        char.db.fire_resistance = 0  # 火系抗性
        char.db.water_resistance = 0  # 水系抗性
        char.db.earth_resistance = 0  # 土系抗性
        char.db.air_resistance = 0  # 风系抗性
        char.db.lightning_resistance = 0  # 雷系抗性
        char.db.ice_resistance = 0  # 冰系抗性
        char.db.light_resistance = 0  # 光系抗性
        char.db.dark_resistance = 0  # 暗系抗性
        needs_migration = True

    # 修仙相关属性
    if not hasattr(char.db, 'cultivation') or char.db.cultivation is None:
        char.db.cultivation = "凡人"  # 境界
        needs_migration = True
    if not hasattr(char.db, 'cultivation_level') or char.db.cultivation_level is None:
        char.db.cultivation_level = 0  # 境界等级
        needs_migration = True
    if not hasattr(char.db, 'spirit_power') or char.db.spirit_power is None:
        char.db.spirit_power = 10  # 灵力
        needs_migration = True

    # 基础属性
    if not hasattr(char.db, 'strength') or char.db.strength is None:
        char.db.strength = 10  # 力量
        needs_migration = True
    if not hasattr(char.db, 'agility') or char.db.agility is None:
        char.db.agility = 10  # 身法
        needs_migration = True
    if not hasattr(char.db, 'intelligence') or char.db.intelligence is None:
        char.db.intelligence = 10  # 悟性
        needs_migration = True
    if not hasattr(char.db, 'constitution') or char.db.constitution is None:
        char.db.constitution = 10  # 根骨
        needs_migration = True

    # 金钱
    if not hasattr(char.db, 'gold') or char.db.gold is None:
        char.db.gold = 10  # 金币
        needs_migration = True
    if not hasattr(char.db, 'silver') or char.db.silver is None:
        char.db.silver = 50  # 银币
        needs_migration = True

    # 已学会的法术列表
    if not hasattr(char.db, 'known_spells') or char.db.known_spells is None:
        char.db.known_spells = ["fireball"]  # 默认只会火球术
        needs_migration = True

    # 法术冷却时间
    if not hasattr(char, 'spell_cooldowns'):
        char.spell_cooldowns = {}
        needs_migration = True

    if needs_migration:
        return "角色已成功添加所有系统属性。"
    else:
        return "角色已经有魔法系统属性，无需迁移。"
