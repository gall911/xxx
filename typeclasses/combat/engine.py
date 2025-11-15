# 战斗核心模块
# 用于处理战斗逻辑和状态管理

def apply_damage(target, damage, damage_type="physical"):
    """对目标造成伤害"""
    if not hasattr(target.db, 'hp'):
        target.db.hp = 100
        
    if not hasattr(target.db, 'max_hp'):
        target.db.max_hp = 100
        
    target.db.hp -= damage
    
    if target.db.hp <= 0:
        target.db.hp = 0
        return True  # 目标死亡
        
    return False  # 目标存活

def is_in_range(caster, target, range_distance):
    """检查目标是否在范围内"""
    # 简单实现：假设在同一房间就是范围内
    return caster.location == target.location

def check_cooldown(caster, spell_key):
    """检查技能是否在冷却中"""
    # 确保冷却字典已初始化
    if not hasattr(caster.db, 'cooldowns') or caster.db.cooldowns is None:
        caster.db.cooldowns = {}
        
    if spell_key in caster.db.cooldowns:
        # 检查冷却是否已经结束
        import time
        if time.time() < caster.db.cooldowns[spell_key]:
            return True
    return False

def set_cooldown(caster, spell_key, cooldown_time):
    """设置技能冷却时间"""
    # 确保冷却字典已初始化
    if not hasattr(caster.db, 'cooldowns') or caster.db.cooldowns is None:
        caster.db.cooldowns = {}
        
    import time
    caster.db.cooldowns[spell_key] = time.time() + cooldown_time