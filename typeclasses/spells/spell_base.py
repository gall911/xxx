from twisted.internet import reactor
from evennia.utils.utils import delay
from typeclasses.spells.loader import load_spell_data, MAGIC_INDEX
class Spell:
    """
    基本法术类
    支持：
      - 多阶段施法
      - 冷却
      - 打断
    """

    active_spells = {}  # 内存里记录正在施法的玩家 key=caller, value=dict

    def __init__(self, caster, spell_key, data, target):
        self.caster = caster
        self.spell_key = spell_key
        self.data = data
        self.target = target
        self.current_stage = 0
        self.total_stages = data.get("stages", [])
        self.skill_level = 1
        if hasattr(caster.db, "skills") and spell_key in caster.db.skills:
            self.skill_level = caster.db.skills[spell_key]["level"]

    def start(self):
        """
        启动施法
        """
        if not self.total_stages:
            self.execute()
            return

        # 注册正在施法
        Spell.active_spells[self.caster] = self

        # 开始第一阶段
        self.next_stage()

    def next_stage(self):
        """
        执行下一个阶段
        """
        if self.current_stage >= len(self.total_stages):
            self.finish()
            return

        stage = self.total_stages[self.current_stage]
        msg = stage.get("msg", "").format(caster=self.caster.key, target=self.target.key)
        delay_time = stage.get("delay", 0)

        # 发消息给玩家和房间
        self.caster.msg(msg)
        if hasattr(self.caster, "location") and self.caster.location:
            self.caster.location.msg_contents(msg, exclude=[self.caster])

        self.current_stage += 1

        if self.current_stage < len(self.total_stages):
            reactor.callLater(delay_time, self.next_stage)
        else:
            # 最后一阶段延迟后执行伤害
            reactor.callLater(delay_time, self.execute)

    def execute(self):
        """
        实际技能效果
        """
        dmg_data = self.data.get("damage", {})
        base = dmg_data.get("base", 0)
        per_level = dmg_data.get("per_level", 0)
        dmg = base + per_level * (self.skill_level - 1)

        if not hasattr(self.target.db, "hp") or self.target.db.hp is None:
            self.target.db.hp = 100

        self.target.db.hp -= dmg
        if self.target.db.hp < 0:
            self.target.db.hp = 0

        # 发送结果消息
        spell_name = self.data.get("name", "未知技能")
        self.caster.msg(f"你施放了{spell_name}，对{self.target.key}造成{dmg}点伤害。")
        self.target.msg(f"{self.caster.key}对你施放了{spell_name}，造成{dmg}点伤害。")
        if self.target.db.hp == 0:
            self.caster.msg(f"{self.target.key}被你击败了！")
            self.target.msg("你被击败了！")

        # 设置技能冷却
        cooldown = self.data.get("cooldown", 0)
        if cooldown > 0:
            from typeclasses.combat.engine import set_cooldown
            set_cooldown(self.caster, self.spell_key, cooldown)
            self.caster.msg(f"{spell_name}进入冷却 {cooldown}秒")

        self.finish()

    def finish(self):
        """
        施法结束，移除记录
        """
        if self.caster in Spell.active_spells:
            del Spell.active_spells[self.caster]

    @staticmethod
    def interrupt(caster):
        """
        外部打断
        """
        spell = Spell.active_spells.get(caster)
        if spell:
            caster.msg("你的施法被打断！")
            if hasattr(caster, "location") and caster.location:
                caster.location.msg_contents(f"{caster.key}的施法被打断！", exclude=[caster])
            spell.finish()
