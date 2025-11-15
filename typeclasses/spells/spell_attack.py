# /home/gg/xxx/typeclasses/spells/spell_attack.py
from .spell_base import SpellBase

class AttackSpell(SpellBase):
    def __init__(self, path, data):
        super().__init__(path, data)

    def finish(self, caster, target):
        # 消耗资源（真元）在这里扣
        cost = self.data.get("cost", 0)
        if cost and getattr(caster.db, "mana", 0) < cost:
            caster.msg("真元不足，施法失败。")
            return
        if cost:
            caster.db.mana = getattr(caster.db, "mana", 0) - cost

        # 计算伤害
        lvl = 1
        skills = getattr(caster.db, "skills", {}) or {}
        if self.path in skills:
            lvl = skills[self.path].get("level", 1)
        dmg_conf = self.data.get("damage", {})
        base = dmg_conf.get("base", 0)
        per = dmg_conf.get("per_level", 0)
        dmg = base + per * (lvl - 1) + getattr(caster.db, "magic_power", 0)

        # 应用伤害（安全处理）
        if not hasattr(target.db, "hp") or target.db.hp is None:
            target.db.hp = 100
        target.db.hp = max(0, target.db.hp - dmg)

        # 通知
        caster.msg(f"你释放了{self.name}，对{target.key}造成 {dmg} 点伤害。")
        target.msg(f"{caster.key} 对你释放了{self.name}，造成 {dmg} 点伤害。")
        caster.location.msg_contents(f"{caster.key} 的{self.name}命中{target.key}！", exclude=[caster, target])
        # 保存死亡/击败逻辑
        if target.db.hp == 0:
            caster.msg(f"{target.key} 被你打败了！")
            target.msg("你被打败了！")
