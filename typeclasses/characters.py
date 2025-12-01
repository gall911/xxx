# typeclasses/characters.py
"""
角色类型类
"""
from evennia import DefaultCharacter
# ❌ 注意：顶部绝对不要 import commands 或 world 下的模块
# from commands.combat import CombatCmdSet      (已移除)
# from world.loaders.game_data import ...       (已移除)

class Character(DefaultCharacter):
    """
    修仙角色类
    继承自Evennia的DefaultCharacter
    """
    
    def at_object_creation(self):
        """角色首次创建时调用"""
        super().at_object_creation()
        
        # ✅ 在这里导入数据加载器 (懒加载)
        from world.loaders.game_data import get_config
        
        # 初始化NDB属性
        self._init_ndb_attributes()
        
        # 从配置获取初始属性
        starting_realm = get_config('player.starting_realm', '练气期')
        starting_stats = get_config('player.starting_stats', {})
        
        self.ndb.realm = starting_realm
        self.ndb.level = 1
        self.ndb.exp = 0
        
        # 设置属性
        self.ndb.hp = starting_stats.get('hp', 100)
        self.ndb.max_hp = starting_stats.get('max_hp', 100)
        self.ndb.qi = starting_stats.get('qi', 50)
        self.ndb.max_qi = starting_stats.get('max_qi', 50)
        self.ndb.strength = starting_stats.get('strength', 10)
        self.ndb.agility = starting_stats.get('agility', 10)
        self.ndb.intelligence = starting_stats.get('intelligence', 10)
        
        self.ndb.skills = ['普通攻击']
        self.ndb.inventory = {'聚气丹': 5, '回春丹': 3}
        self.ndb.in_combat = False
        self.ndb.combat_target = None
        
        self._apply_realm_bonuses()
    
    def at_init(self):
        """对象从数据库加载时调用"""
        super().at_init()
        self._init_ndb_attributes()
        self._load_from_db()
    
    def _init_ndb_attributes(self):
        """初始化所有NDB属性"""
        # (保持原样，省略重复代码以节省篇幅，逻辑不用变)
        if not hasattr(self.ndb, 'hp'): self.ndb.hp = 100
        if not hasattr(self.ndb, 'max_hp'): self.ndb.max_hp = 100
        if not hasattr(self.ndb, 'qi'): self.ndb.qi = 50
        if not hasattr(self.ndb, 'max_qi'): self.ndb.max_qi = 50
        if not hasattr(self.ndb, 'strength'): self.ndb.strength = 10
        if not hasattr(self.ndb, 'agility'): self.ndb.agility = 10
        if not hasattr(self.ndb, 'intelligence'): self.ndb.intelligence = 10
        if not hasattr(self.ndb, 'level'): self.ndb.level = 1
        if not hasattr(self.ndb, 'exp'): self.ndb.exp = 0
        if not hasattr(self.ndb, 'realm'): self.ndb.realm = '练气期'
        if not hasattr(self.ndb, 'skills'): self.ndb.skills = []
        if not hasattr(self.ndb, 'inventory'): self.ndb.inventory = {}
        if not hasattr(self.ndb, 'in_combat'): self.ndb.in_combat = False
        if not hasattr(self.ndb, 'combat_target'): self.ndb.combat_target = None
        if not hasattr(self.ndb, 'buffs'): self.ndb.buffs = []
        if not hasattr(self.ndb, 'debuffs'): self.ndb.debuffs = []
        if not hasattr(self.ndb, 'dots'): self.ndb.dots = []
    
    def _load_from_db(self):
        """从数据库加载保存的数据"""
        saved_data = self.db.character_data
        if not saved_data:
            return
        # (保持原样)
        self.ndb.hp = saved_data.get('hp', self.ndb.hp)
        self.ndb.max_hp = saved_data.get('max_hp', self.ndb.max_hp)
        self.ndb.qi = saved_data.get('qi', self.ndb.qi)
        self.ndb.max_qi = saved_data.get('max_qi', self.ndb.max_qi)
        self.ndb.level = saved_data.get('level', self.ndb.level)
        self.ndb.exp = saved_data.get('exp', self.ndb.exp)
        self.ndb.realm = saved_data.get('realm', self.ndb.realm)
        self.ndb.strength = saved_data.get('strength', self.ndb.strength)
        self.ndb.agility = saved_data.get('agility', self.ndb.agility)
        self.ndb.intelligence = saved_data.get('intelligence', self.ndb.intelligence)
        self.ndb.skills = saved_data.get('skills', self.ndb.skills)
        self.ndb.inventory = saved_data.get('inventory', self.ndb.inventory)
    
    def _apply_realm_bonuses(self):
        """应用境界属性加成"""
        # ✅ 在这里导入数据加载器
        from world.loaders.game_data import get_data
        
        realm_data = get_data('realms', self.ndb.realm)
        if not realm_data:
            return
        
        bonuses = realm_data.get('attribute_bonus', {})
        for attr, value in bonuses.items():
            if hasattr(self.ndb, attr):
                current = getattr(self.ndb, attr)
                setattr(self.ndb, attr, current + value)
        
        max_qi = realm_data.get('max_qi')
        if max_qi:
            self.ndb.max_qi = max_qi
    
    def at_before_move(self, destination, **kwargs):
        if self.ndb.in_combat:
            self.msg("战斗中无法移动！")
            return False
        if getattr(self.ndb, 'is_cultivating', False):
            self.msg("请先停止修炼。")
            return False
        return True
    
    def at_object_receive(self, moved_obj, source_location, **kwargs):
        pass
    
    def return_appearance(self, looker, **kwargs):
        text = super().return_appearance(looker, **kwargs)
        realm = getattr(self.ndb, 'realm', '未知')
        level = getattr(self.ndb, 'level', 1)
        text += f"\n境界: |c{realm}|n  等级: |y{level}|n"
        if self.ndb.in_combat:
            text += f"\n|r【战斗中】|n"
        return text
    
    def at_post_puppet(self, **kwargs):
        """玩家连接到角色后"""
        super().at_post_puppet(**kwargs)
        
        # ✅ 重点：在这里导入所有的命令集
        # 这样只有在游戏运行、玩家登录时才会加载，绝对不会在启动时报错
        from commands.combat import CombatCmdSet
        from commands.cultivation import CultivationCmdSet
        from commands.inventory import InventoryCmdSet
        # 如果你想恢复 DevCmdSet，也可以在这里加:
        # from commands.dev.dev_cmdset import DevCmdSet
        # self.cmdset.add(DevCmdSet, persistent=True)

        # 添加命令集
        self.cmdset.add(CombatCmdSet, persistent=True)
        self.cmdset.add(CultivationCmdSet, persistent=True)
        self.cmdset.add(InventoryCmdSet, persistent=True)
        
        # 欢迎消息
        self.msg("|c" + "=" * 60)
        self.msg(f"欢迎回来，{self.key}！")
        self.msg(f"境界: |y{self.ndb.realm}|n  等级: |y{self.ndb.level}|n")
        self.msg(f"生命: |g{self.ndb.hp}/{self.ndb.max_hp}|n  灵力: |c{self.ndb.qi}/{self.ndb.max_qi}|n")
        self.msg("|c" + "=" * 60)
        self.msg("\n输入 |w帮助|n 查看可用命令")
        self.msg("输入 |w状态|n 查看详细属性\n")