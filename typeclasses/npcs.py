"""
typeclasses/npcs.py
NPC与怪物定义
"""
from typeclasses.characters import Character
from world.systems.attr_manager import AttrManager

class NPC(Character):
    """
    [剧情NPC]
    拥有持久化数据，通常用于对话、商店、任务发布。
    """
    is_npc = True 

    def at_object_creation(self):
        # 1. 调用父类初始化 (加载 YAML 属性 -> db -> ndb)
        super().at_object_creation()
        
        self.db.is_aggressive = False
        self.db.ai_type = "passive"
        
        # 2. 应用特定配置
        self._init_npc_stats()

    def at_init(self):
        super().at_init()
        self.is_npc = True

    def _init_npc_stats(self):
        """加载 yaml 中定义的 stats 到 db"""
        stats = self.db.stats or {}
        for key, val in stats.items():
            if self.attributes.has(key):
                self.attributes.add(key, val)
                # 同步上限
                if self.attributes.has(f"max_{key}"):
                    self.attributes.add(f"max_{key}", val)
        
        # 更新完 db 后，强制同步一次 ndb，确保内存数据最新
        self.sync_stats_to_ndb()


class Monster(NPC):
    """
    [怪物/Combat Mob]
    专注于战斗，虽然技术上它也有 db 属性(Evennia限制)，
    但我们在逻辑上视为"全内存战斗单位"。
    """
    def at_object_creation(self):
        super().at_object_creation()
        self.db.is_aggressive = True
        self.db.ai_type = "combat"
        # 怪物死亡后不保留尸体，直接清理（可选）
        # self.db.clean_on_death = True 

    def at_init(self):
        super().at_init()
        # 怪物初始化时，确保满状态
        if self.db.max_hp:
            self.ndb.hp = self.db.max_hp
        if self.db.max_qi:
            self.ndb.qi = self.db.max_qi

    def sync_stats_to_ndb(self):
        """
        怪物可以有特殊的同步逻辑，比如增加随机浮动
        """
        super().sync_stats_to_ndb()
        # 示例：怪物血量可能有 5% 浮动
        # import random
        # self.ndb.max_hp = int(self.ndb.max_hp * random.uniform(0.95, 1.05))
        # self.ndb.hp = self.ndb.max_hp