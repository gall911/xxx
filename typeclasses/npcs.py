"""
NPC类型类
typeclasses/npcs.py
"""
from typeclasses.characters import Character

class NPC(Character):
    is_npc = True 

    def at_object_creation(self):
        """NPC创建时初始化"""
        super().at_object_creation()
        
        self.db.is_aggressive = False
        self.is_npc = True
        self.db.ai_type = "passive"
        self.db.respawn_time = 300  # 5分钟重生
        self.db.spawn_location = None
        
        self._init_ndb_attributes()

    def at_init(self):
        """
        服务器重启(@reload)时会自动调用
        必须在这里重新加载 ndb 属性
        """
        super().at_init()
        self.is_npc = True
        self._init_ndb_attributes()

    def _init_ndb_attributes(self):
        """初始化内存(NDB)属性"""
        stats = self.db.stats or {}
        
        # 1. 基础战斗数值
        if not hasattr(self.ndb, 'hp'):
            self.ndb.max_hp = stats.get('max_hp', 100)
            self.ndb.hp = self.ndb.max_hp
            
        if not hasattr(self.ndb, 'qi'):
            self.ndb.max_qi = stats.get('max_qi', 100)
            self.ndb.qi = self.ndb.max_qi

        # 2. 其他属性
        self.ndb.level = stats.get('level', 1)
        self.ndb.strength = stats.get('strength', 10)
        self.ndb.agility = stats.get('agility', 10)
        
        # ========== 新增：反击率属性 ==========
        self.ndb.counter_rate = 0.0  # 基础反击率（由装备+被动技能动态计算）
        
        # 3. 战斗状态标记
        if not hasattr(self.ndb, 'in_combat'):
            self.ndb.in_combat = False
        self.ndb.combat_target = None
        
        # 4. 技能列表
        self.ndb.skills = self.db.skills or ['普通攻击']
        self.ndb.passive_skills = self.db.passive_skills or []
        self.ndb.drops = self.db.drops or []