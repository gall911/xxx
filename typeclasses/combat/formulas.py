# 伤害计算公式

def calculate_damage(base_damage, per_level, level, caster_level=1):
    """计算技能伤害"""
    # 基础伤害 + 等级加成
    damage = base_damage + (per_level * level)
    
    # 可以添加更多计算因素，如角色属性加成等
    # damage *= (1 + caster_level * 0.05)  # 示例：角色等级加成
    
    return int(damage)

def calculate_healing(base_heal, per_level, level, caster_level=1):
    """计算治疗量"""
    healing = base_heal + (per_level * level)
    
    # 可以添加更多计算因素
    # healing *= (1 + caster_level * 0.05)
    
    return int(healing)