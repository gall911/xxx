
# 火系法术实现
from evennia.utils import search as default_search
from typeclasses.characters import Character
from world.magic.spells.base_spell import BaseSpell

class Fireball(BaseSpell):
    """
    火球术 - 一个基础的火系攻击法术
    """

    def at_object_creation(self):
        super().at_object_creation()
        self.db.name = "火球术"
        self.db.key = "fireball"
        self.db.description = "召唤一个炽热的火球攻击目标。"
        self.db.mana_cost = 10  # 法力消耗
        self.db.damage = 20     # 基础伤害值
        self.db.element = "fire"  # 元素属性
        self.db.level = 1       # 法术等级

    def cast(self, caster, target=None):
        """
        施放火球术

        Args:
            caster (Character): 施法者
            target (Character or None): 目标，如果没有指定则随机选择

        Returns:
            tuple: (success, message) - 是否成功及结果消息
        """
        # 检查法力值是否足够
        # 确保角色有法力值属性
        if caster.db.mana is None:
            caster.db.mana = 100  # 默认法力值
            
        mana_cost = getattr(self.db, 'mana_cost', 10)  # 默认10点法力
        if caster.db.mana < mana_cost:
            return False, f"你的法力不足，需要{mana_cost}点法力才能施放{self.db.name}。"

        # 如果没有指定目标，尝试从当前房间获取
        if not target:
            # 获取当前房间内的其他角色
            targets = [obj for obj in caster.location.contents 
                      if isinstance(obj, Character) and obj != caster]
            if not targets:
                return False, "这里没有可以施放火球术的目标。"
            target = targets[0]  # 选择第一个目标

        # 消耗法力值
        caster.db.mana -= mana_cost

        # 计算实际伤害（考虑法术强度、目标抗性等）
        actual_damage = self.calculate_damage(caster, target)

        # 应用伤害
        if target.db.hp is None:
            target.db.hp = 100  # 默认生命值
        target.db.hp -= actual_damage

        # 构建施法消息
        caster_msg = f"你施放了{self.db.name}，一个炽热的火球飞向{target.key}，造成了{actual_damage}点伤害！"
        target_msg = f"{caster.key}对你施放了{self.db.name}，火球爆炸造成{actual_damage}点伤害！"
        room_msg = f"{caster.key}对{target.key}施放了{self.db.name}，一团炽热的火焰在{target.key}身上炸开！"

        # 发送消息
        caster.msg(caster_msg)
        target.msg(target_msg)
        caster.location.msg_contents(room_msg, exclude=[caster, target])

        return True, caster_msg

    def calculate_damage(self, caster, target):
        """
        计算实际伤害值

        Args:
            caster (Character): 施法者
            target (Character): 目标

        Returns:
            int: 实际伤害值
        """
        # 基础伤害
        damage = self.db.damage

        # 考虑施法者的魔法强度
        if caster.db.magic_power is not None:
            damage += caster.db.magic_power

        # 考虑目标的火系抗性
        if target.db.fire_resistance is not None:
            damage = max(1, damage - target.db.fire_resistance)

        # 随机浮动 (±20%)
        import random
        damage = int(damage * random.uniform(0.8, 1.2))

        return damage
