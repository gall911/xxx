"""
NPC类型类
typeclasses/npcs.py
"""
from typeclasses.characters import Character

class NPC(Character):
    # 【修复1】类属性放这里，不需要缩进太深
    is_npc = True 

    def at_object_creation(self):
        """NPC创建时初始化"""
        # 先调用父类初始化（这会初始化ndb属性）
        super().at_object_creation()
        
        # 【修复2】下面的缩进全部统一向左对齐，否则Python不认
        self.db.is_aggressive = False
        
        # 标记为NPC
        # (其实有上面的类属性就够了，但为了保险起见保留你的写法)
        self.is_npc = True
        
        # AI类型
        self.db.ai_type = "passive"  # passive, aggressive, neutral
        
        # 刷新相关
        self.db.respawn_time = 300  # 5分钟重生
        self.db.spawn_location = None
        
        # 确保NDB属性已初始化
        self._init_ndb_attributes()

    def at_init(self):
        """
        【重要】服务器重启(@reload)时会自动调用
        必须在这里重新加载 ndb 属性，否则重启后NPC血量和技能会丢失
        """
        super().at_init()
        # 再次确认是NPC (防止重载后丢失标签)
        self.is_npc = True
        self._init_ndb_attributes()

    def _init_ndb_attributes(self):
        """
        【补充】初始化内存(NDB)属性
        这是你在 at_object_creation 里调用的那个函数
        """
        # 读取 yaml 生成时存入的 stats，如果没存则用空字典
        stats = self.db.stats or {}
        
        # 1. 基础战斗数值 (如果内存里没有，就从数据库读)
        if not hasattr(self.ndb, 'hp'):
            self.ndb.max_hp = stats.get('max_hp', 100)
            self.ndb.hp = self.ndb.max_hp  # 默认满血
            
        if not hasattr(self.ndb, 'qi'):
            self.ndb.max_qi = stats.get('max_qi', 100)
            self.ndb.qi = self.ndb.max_qi

        # 2. 其他属性
        self.ndb.level = stats.get('level', 1)
        self.ndb.strength = stats.get('strength', 10)
        self.ndb.agility = stats.get('agility', 10)
        
        # 3. 战斗状态标记
        if not hasattr(self.ndb, 'in_combat'):
            self.ndb.in_combat = False
        self.ndb.combat_target = None
        
        # 4. 技能列表
        self.ndb.skills = self.db.skills or ['普通攻击']
        self.ndb.passive_skills = self.db.passive_skills or []
        self.ndb.drops = self.db.drops or []