import os
import time
import yaml
from evennia import utils

# 缓存已加载的 skill 数据
_SKILL_CACHE = {}

def _load_skill_group(group):
    """从 world/magic/<group>.yaml 加载并缓存"""
    if group in _SKILL_CACHE:
        return _SKILL_CACHE[group]
    basepath = os.path.join(os.path.dirname(__file__), "..", "world", "magic")
    path = os.path.normpath(os.path.join(basepath, f"{group}.yaml"))
    if not os.path.exists(path):
        _SKILL_CACHE[group] = {}
        return _SKILL_CACHE[group]
    with open(path, "r", encoding="utf8") as f:
        data = yaml.safe_load(f) or {}
    # 支持 _base 继承：把 _base 合并到每个技能
    base = data.get("_base", {}) or {}
    for k, v in data.items():
        if k == "_base":
            continue
        merged = dict(base)
        if isinstance(v, dict):
            merged.update(v)
        else:
            merged.update({"value": v})
        data[k] = merged
    _SKILL_CACHE[group] = data
    return data

def parse_skill_path(path):
    """
    支持 'group>id' 或 'id' 两种格式（后者依赖外部解析）。
    Returns (group, id)
    """
    if ">" in path:
        g, k = path.split(">", 1)
        return g.strip(), k.strip()
    # 默认 group 为 'global'（你可以改）
    return "global", path.strip()

def get_skill_config_by_path(path):
    """
    path: "fire>ib" 或 "ib" （若只写 ib，外部应传入完整 path）
    返回技能配置 dict 或 None
    """
    group, sid = parse_skill_path(path)
    data = _load_skill_group(group)
    return data.get(sid)

class SpellBase:
    """基类：持有 config，提供 start_casting 和 finish（子类可覆写）"""
    def __init__(self, config):
        self.key = config.get("name", "unknown")
        self.id = config.get("id") or config.get("key")
        self.config = config
        # 读取常用属性
        self.cost = config.get("cost", 0)
        self.cast_time = config.get("cast_time", 0)   # 可选总吟唱时间（不强制）
        self.cd = config.get("cooldown", 0)  # 使用cooldown而不是cd以匹配现有系统
        self.type = config.get("type", "attack")

    def _format(self, text, caster=None, target=None):
        """简单占位替换：{caster} {target}"""
        if not text:
            return ""
        out = text.replace("{caster}", getattr(caster, "key", "某人"))
        out = out.replace("{target}", getattr(target, "key", "某物"))
        return out

    def start_casting(self, caster, target):
        """
        分阶段施法。配置中应有 'stages': list of {msg: str, delay: seconds_to_next}
        我们会按 stages 逐个发 msg，最后调用 self.finish()
        """
        # 检查资源（简单示例）
        if self.cost and getattr(caster.db, "mp", 0) < self.cost:
            caster.msg("你的魔法值不足，无法施法。")
            return

        # 记录cast状态（用于中断判断）
        cast_id = f"cast#{time.time()}"
        caster.ndb.casting = {"id": cast_id, "spell": self}

        stages = self.config.get("stages", [])
        # 如果没有 stages，则直接 finish
        if not stages:
            # 立即生效（如果需要延迟可在 config 指定 cast_time）
            self.finish(caster, target)
            caster.ndb.casting = None
            return

        # 执行第一阶段并安排后续
        total_delay = 0.0
        for idx, st in enumerate(stages):
            msg = self._format(st.get("msg", ""), caster, target)
            delay_to_next = float(st.get("delay", 0))
            # schedule a callback at total_delay to deliver this stage's msg
            def _mk_stage(msg_local):
                def _stage_cb():
                    # 施法被打断检查
                    cur = getattr(caster.ndb, "casting", None)
                    if not cur or cur.get("id") != cast_id:
                        # 被打断或取消，不继续
                        return
                    # broadcast stage message to room
                    if msg_local:
                        caster.location.msg_contents(msg_local)
                return _stage_cb
            utils.delay(total_delay, _mk_stage(msg))
            total_delay += delay_to_next

        # after all stages, schedule finish callback
        def _finish_cb():
            cur = getattr(caster.ndb, "casting", None)
            if not cur or cur.get("id") != cast_id:
                return
            # consume resource & set cooldown
            if self.cost:
                caster.db.mp = getattr(caster.db, "mp", 0) - self.cost
            # clear casting state
            caster.ndb.casting = None
            # finish effect
            self.finish(caster, target)
            # set cooldown
            cds = getattr(caster.db, "cooldowns", {}) or {}
            cds[self.config.get("path")] = time.time() + self.cd
            caster.db.cooldowns = cds
        utils.delay(total_delay, _finish_cb)

    def finish(self, caster, target):
        """默认 finish：子类或配置覆盖实现效果"""
        # 默认为简单信息
        caster.location.msg_contents(
            f"{caster.key} 施放了 {self.key}，但什么也没发生（未实现 finish）。"
        )

class AttackSpell(SpellBase):
    def finish(self, caster, target):
        # 简单伤害实现（可扩展命中/抗性/暴击）
        # 使用现有系统的伤害计算方式
        damage_data = self.config.get("damage", {})
        base_damage = damage_data.get("base", 0)
        per_level_damage = damage_data.get("per_level", 0)
        
        # 获取施法者技能等级
        skill_level = 1
        if hasattr(caster.db, 'skills') and self.config.get("path") in caster.db.skills:
            skill_level = caster.db.skills[self.config.get("path")]["level"]
        
        # 计算伤害
        dmg = base_damage + per_level_damage * (skill_level - 1)
        
        # 应用伤害
        if not hasattr(target.db, 'hp') or target.db.hp is None:
            target.db.hp = 100  # 默认HP为100
            
        target.db.hp -= dmg
        
        # 确保HP不会低于0
        if target.db.hp < 0:
            target.db.hp = 0
            
        # 发送消息
        caster.location.msg_contents(f"{caster.key} 的 {self.key} 命中 {target.key}，造成 {dmg} 点伤害。")
        
        # 如果目标HP为0，发送死亡消息
        if target.db.hp == 0:
            caster.location.msg_contents(f"{target.key}被{caster.key}击败了！")

# type map
_TYPE_MAP = {
    "attack": AttackSpell,
    "damage": AttackSpell,
    # add "heal": HealSpell etc.
}

def create_spell_from_path(path):
    """
    path: 'fire>ib' or 'fire>fb'
    returns a SpellBase (or subclass) instance with config, or None
    """
    # load config
    group, sid = parse_skill_path(path)
    data = _load_skill_group(group)
    conf = data.get(sid)
    if not conf:
        return None
    # attach path for cooldown key
    conf["path"] = f"{group}>{sid}"
    conf["id"] = sid
    # choose class
    stype = conf.get("type", "attack")
    cls = _TYPE_MAP.get(stype, SpellBase)
    return cls(conf)