"""
typeclasses/characters.py
完整版 - 包含技能槽系统
"""
from evennia import DefaultCharacter
from world.loaders.game_data import get_config, get_data

class Character(DefaultCharacter):
    
    def at_object_creation(self):
        """角色创建时初始化"""
        super().at_object_creation()
        self._init_ndb_attributes()
        
        starting_realm = get_config('player.starting_realm', '练气期')
        starting_stats = get_config('player.starting_stats', {})
        
        # === 基础属性 ===
        self.ndb.realm = starting_realm
        self.ndb.level = 1
        self.ndb.exp = 0
        self.ndb.hp = starting_stats.get('hp', 100)
        self.ndb.max_hp = starting_stats.get('max_hp', 100)
        self.ndb.qi = starting_stats.get('qi', 50)
        self.ndb.max_qi = starting_stats.get('max_qi', 50)
        self.ndb.strength = starting_stats.get('strength', 10)
        self.ndb.agility = starting_stats.get('agility', 10)
        self.ndb.intelligence = starting_stats.get('intelligence', 10)
        
        # === 技能系统（新增） ===
        # 已学会的技能 {skill_key: level}
        self.db.learned_skills = {
            'basic_attack': 1  # 默认会普通攻击
        }
        
        # 技能槽配置
        self.db.skill_slots = {
            'inner': None,       # 内功心法槽（被动）
            'movement': None,    # 身法槽（被动）
            'attack1': None,     # 攻击技能槽1（主动）
            'attack2': None,     # 攻击技能槽2（主动）
        }
        
        # 装备提供的技能槽（额外）
        self.db.equipment_skill_slots = {
            'weapon_skill': None,    # 武器技能槽
            'armor_skill': None,     # 护甲技能槽
        }
        
        # === 旧系统兼容（逐步废弃） ===
        self.ndb.skills = ['basic_attack']  # 旧版技能列表
        self.ndb.inventory = {'聚气丹': 5, '回春丹': 3}
        self.ndb.in_combat = False
        self.ndb.combat_target = None
        
        self._apply_realm_bonuses()
    
    def at_init(self):
        """
        每次服务器Reload或重启，对象被加载进内存时都会运行此方法。
        这是挂载临时命令集最安全的地方。
        """
        super().at_init()
        self._init_ndb_attributes()
        self._load_from_db()
        
        # 加载开发命令集
        self._load_dev_cmdset()
        
        # ========== 新增：应用已装备的被动技能效果 ==========
        self._apply_equipped_passive_skills()

    def at_post_puppet(self, **kwargs):
        """玩家登录时调用"""
        super().at_post_puppet(**kwargs)
        
        # 登录时也检查一下，双保险
        self._load_dev_cmdset()
        
        # 加载命令集
        try:
            from commands.combat import CombatCmdSet
            self.cmdset.add(CombatCmdSet, persistent=True)
        except ImportError: 
            pass
            
        try:
            from commands.cultivation import CultivationCmdSet
            self.cmdset.add(CultivationCmdSet, persistent=True)
        except ImportError: 
            pass

        try:
            from commands.inventory import InventoryCmdSet
            self.cmdset.add(InventoryCmdSet, persistent=True)
        except ImportError: 
            pass
        
        # ========== 新增：加载技能命令集 ==========
        try:
            from commands.skill_commands import SkillCmdSet
            self.cmdset.add(SkillCmdSet, persistent=True)
        except ImportError:
            pass
        
        self.msg("|c" + "=" * 60)
        self.msg(f"欢迎回来，{self.key}！")
        self.msg(f"境界: |y{self.ndb.realm}|n  等级: |y{self.ndb.level}|n")
        self.msg("|c" + "=" * 60)

    def _load_dev_cmdset(self):
        """加载开发命令集"""
        if self.id == 1 or self.is_superuser:
            try:
                from commands.dev.dev_cmdset import DevCmdSet
                self.cmdset.add(DevCmdSet, persistent=False)
            except Exception as e:
                print(f"DevCmdSet Error: {e}")
    
    # ========================================
    # 技能槽系统方法
    # ========================================
    
    def learn_skill(self, skill_key, initial_level=1):
        """
        学习技能
        
        Args:
            skill_key (str): 技能key
            initial_level (int): 初始等级
        
        Returns:
            bool: 是否学习成功
        """
        skill_data = get_data('skills', skill_key)
        if not skill_data:
            self.msg(f"|r找不到技能: {skill_key}|n")
            return False
        
        # 检查是否已学会
        if skill_key in (self.db.learned_skills or {}):
            self.msg(f"|y你已经学会了 {skill_data['name']}！|n")
            return False
        
        # 检查学习条件
        required_realm = skill_data.get('required_realm')
        required_level = skill_data.get('required_level', 1)
        required_skills = skill_data.get('required_skills', [])
        
        # 检查境界
        if required_realm and self.ndb.realm != required_realm:
            # TODO: 更精确的境界比较
            pass
        
        # 检查等级
        if self.ndb.level < required_level:
            self.msg(f"|r需要等级 {required_level} 才能学习此技能！|n")
            return False
        
        # 检查前置技能
        for prereq_skill in required_skills:
            if prereq_skill not in (self.db.learned_skills or {}):
                prereq_data = get_data('skills', prereq_skill)
                prereq_name = prereq_data.get('name', prereq_skill) if prereq_data else prereq_skill
                self.msg(f"|r需要先学会 {prereq_name}！|n")
                return False
        
        # 学会技能
        if not hasattr(self.db, 'learned_skills') or self.db.learned_skills is None:
            self.db.learned_skills = {}
        
        self.db.learned_skills[skill_key] = initial_level
        self.msg(f"|g你学会了 {skill_data['name']} Lv{initial_level}！|n")
        
        # TODO: 消耗学习材料/金币
        
        return True
    
    def upgrade_skill(self, skill_key):
        """
        升级技能
        
        Args:
            skill_key (str): 技能key
        
        Returns:
            bool: 是否升级成功
        """
        learned_skills = self.db.learned_skills or {}
        
        if skill_key not in learned_skills:
            self.msg("|r你还没学会这个技能！|n")
            return False
        
        current_level = learned_skills[skill_key]
        skill_data = get_data('skills', skill_key)
        
        if not skill_data:
            self.msg("|r技能数据不存在！|n")
            return False
        
        max_level = skill_data.get('level_formula', {}).get('max_level', 1)
        
        if current_level >= max_level:
            self.msg(f"|y{skill_data['name']} 已经满级（Lv{max_level}）！|n")
            return False
        
        # TODO: 检查升级条件（消耗物品/金币/经验）
        
        self.db.learned_skills[skill_key] += 1
        new_level = self.db.learned_skills[skill_key]
        
        self.msg(f"|g{skill_data['name']} 升级到 Lv{new_level}！|n")
        
        # 如果技能已装备，重新应用被动效果
        if skill_key in self.db.skill_slots.values():
            self._apply_equipped_passive_skills()
        
        return True
    
    def equip_skill(self, slot_name, skill_key):
        """
        装备技能到技能槽
        
        Args:
            slot_name (str): 技能槽名称
            skill_key (str): 技能key
        
        Returns:
            bool: 是否装备成功
        """
        # 初始化技能槽
        if not hasattr(self.db, 'skill_slots') or self.db.skill_slots is None:
            self.db.skill_slots = {
                'inner': None,
                'movement': None,
                'attack1': None,
                'attack2': None,
            }
        
        # 检查是否学会
        if skill_key not in (self.db.learned_skills or {}):
            self.msg("|r你还没学会这个技能！|n")
            return False
        
        # 检查技能槽是否存在
        if slot_name not in self.db.skill_slots:
            self.msg(f"|r不存在技能槽: {slot_name}|n")
            self.msg("可用槽位: inner, movement, attack1, attack2")
            return False
        
        skill_data = get_data('skills', skill_key)
        if not skill_data:
            self.msg("|r技能数据不存在！|n")
            return False
        
        # 检查技能类型匹配
        skill_type = skill_data.get('type')
        
        if slot_name in ['inner', 'movement']:
            if skill_type != 'passive':
                self.msg(f"|r{slot_name} 槽位只能装备被动技能！|n")
                return False
        
        if slot_name.startswith('attack'):
            if skill_type != 'active':
                self.msg(f"|r{slot_name} 槽位只能装备主动技能！|n")
                return False
        
        # 卸下旧技能
        old_skill = self.db.skill_slots.get(slot_name)
        if old_skill:
            self._remove_passive_skill_effect(old_skill)
            old_data = get_data('skills', old_skill)
            if old_data:
                self.msg(f"|y卸下了 {old_data['name']}|n")
        
        # 装备新技能
        self.db.skill_slots[slot_name] = skill_key
        self.msg(f"|g装备了 {skill_data['name']} 到 {slot_name}！|n")
        
        # 应用被动技能效果
        if skill_type == 'passive':
            self._apply_passive_skill_effect(skill_key)
        
        # 同步到旧系统（逐步废弃）
        self._sync_to_old_skill_system()
        
        return True
    
    def unequip_skill(self, slot_name):
        """
        卸下技能槽的技能
        
        Args:
            slot_name (str): 技能槽名称
        
        Returns:
            bool: 是否卸下成功
        """
        if not hasattr(self.db, 'skill_slots') or self.db.skill_slots is None:
            self.msg("|r技能槽未初始化！|n")
            return False
        
        if slot_name not in self.db.skill_slots:
            self.msg(f"|r不存在技能槽: {slot_name}|n")
            return False
        
        skill_key = self.db.skill_slots.get(slot_name)
        
        if not skill_key:
            self.msg(f"|y槽位 {slot_name} 已经是空的！|n")
            return False
        
        skill_data = get_data('skills', skill_key)
        
        # 移除被动技能效果
        if skill_data and skill_data.get('type') == 'passive':
            self._remove_passive_skill_effect(skill_key)
        
        self.db.skill_slots[slot_name] = None
        
        if skill_data:
            self.msg(f"|g卸下了 {skill_data['name']}|n")
        
        # 同步到旧系统
        self._sync_to_old_skill_system()
        
        return True
    
    def _apply_equipped_passive_skills(self):
        """应用所有已装备的被动技能效果"""
        if not hasattr(self.db, 'skill_slots'):
            return
        
        for slot_name, skill_key in self.db.skill_slots.items():
            if skill_key:
                skill_data = get_data('skills', skill_key)
                if skill_data and skill_data.get('type') == 'passive':
                    self._apply_passive_skill_effect(skill_key, silent=True)
    
    def _apply_passive_skill_effect(self, skill_key, silent=False):
        """
        应用被动技能的属性加成
        
        Args:
            skill_key (str): 技能key
            silent (bool): 是否静默（不显示消息）
        """
        skill_data = get_data('skills', skill_key)
        if not skill_data:
            return
        
        effects = skill_data.get('effects', [])
        
        for effect in effects:
            if effect.get('type') == 'stat_bonus':
                stat_name = effect['stat']
                value = effect['value']
                
                # 增加属性
                current_value = getattr(self.ndb, stat_name, 0) or 0
                setattr(self.ndb, stat_name, current_value + value)
                
                if not silent:
                    if value > 0:
                        self.msg(f"|g{stat_name} +{value}|n")
                    else:
                        self.msg(f"|r{stat_name} {value}|n")
    
    def _remove_passive_skill_effect(self, skill_key):
        """
        移除被动技能的属性加成
        
        Args:
            skill_key (str): 技能key
        """
        skill_data = get_data('skills', skill_key)
        if not skill_data:
            return
        
        effects = skill_data.get('effects', [])
        
        for effect in effects:
            if effect.get('type') == 'stat_bonus':
                stat_name = effect['stat']
                value = effect['value']
                
                # 减少属性
                current_value = getattr(self.ndb, stat_name, 0) or 0
                setattr(self.ndb, stat_name, current_value - value)
                
                if value > 0:
                    self.msg(f"|y{stat_name} -{value}|n")
    
    def get_equipped_skills(self):
        """
        获取所有已装备的技能
        
        Returns:
            dict: {slot_name: (skill_key, skill_level)}
        """
        result = {}
        
        skill_slots = self.db.skill_slots or {}
        learned_skills = self.db.learned_skills or {}
        
        for slot_name, skill_key in skill_slots.items():
            if skill_key:
                level = learned_skills.get(skill_key, 1)
                result[slot_name] = (skill_key, level)
        
        # 加上装备提供的技能
        equipment_slots = self.db.equipment_skill_slots or {}
        for slot_name, skill_key in equipment_slots.items():
            if skill_key:
                level = 1  # 装备技能默认1级
                result[slot_name] = (skill_key, level)
        
        return result
    
    def get_active_skills(self):
        """
        获取所有可用的主动技能（用于战斗）
        
        Returns:
            list: [(skill_key, skill_level), ...]
        """
        result = []
        
        skill_slots = self.db.skill_slots or {}
        learned_skills = self.db.learned_skills or {}
        
        for slot_name, skill_key in skill_slots.items():
            if skill_key and slot_name.startswith('attack'):
                level = learned_skills.get(skill_key, 1)
                result.append((skill_key, level))
        
        # 加上装备技能
        equipment_slots = self.db.equipment_skill_slots or {}
        for slot_name, skill_key in equipment_slots.items():
            if skill_key:
                result.append((skill_key, 1))
        
        return result
    
    def _sync_to_old_skill_system(self):
        """同步到旧的技能系统（向后兼容）"""
        active_skills = [key for key, level in self.get_active_skills()]
        self.ndb.skills = active_skills if active_skills else ['basic_attack']
    
    # ========================================
    # 原有方法（保持不变）
    # ========================================
    
    def _init_ndb_attributes(self):
        """初始化内存属性"""
        if not hasattr(self.ndb, 'hp'): 
            self.ndb.hp = 100
        if not hasattr(self.ndb, 'max_hp'): 
            self.ndb.max_hp = 100
        if not hasattr(self.ndb, 'qi'): 
            self.ndb.qi = 50
        if not hasattr(self.ndb, 'max_qi'): 
            self.ndb.max_qi = 50
        if not hasattr(self.ndb, 'strength'): 
            self.ndb.strength = 10
        if not hasattr(self.ndb, 'agility'): 
            self.ndb.agility = 10
        if not hasattr(self.ndb, 'intelligence'): 
            self.ndb.intelligence = 10
        if not hasattr(self.ndb, 'level'): 
            self.ndb.level = 1
        if not hasattr(self.ndb, 'exp'): 
            self.ndb.exp = 0
        if not hasattr(self.ndb, 'realm'): 
            self.ndb.realm = '练气期'
        if not hasattr(self.ndb, 'skills'): 
            self.ndb.skills = []
        if not hasattr(self.ndb, 'inventory'): 
            self.ndb.inventory = {}
        if not hasattr(self.ndb, 'in_combat'): 
            self.ndb.in_combat = False
        if not hasattr(self.ndb, 'combat_target'): 
            self.ndb.combat_target = None
        if not hasattr(self.ndb, 'buffs'): 
            self.ndb.buffs = []
        if not hasattr(self.ndb, 'debuffs'): 
            self.ndb.debuffs = []
        if not hasattr(self.ndb, 'dots'): 
            self.ndb.dots = []
        if not hasattr(self.ndb, 'is_cultivating'): 
            self.ndb.is_cultivating = False
        
        # ========== 新增：反击率初始化 ==========
        if not hasattr(self.ndb, 'counter_rate'):
            self.ndb.counter_rate = 0.0
        if not hasattr(self.ndb, 'dodge_rate'):
            self.ndb.dodge_rate = 0.1
    
    def _load_from_db(self):
        """从数据库加载数据"""
        saved_data = self.db.character_data
        if not saved_data: 
            return
        
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
        """应用境界加成"""
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
        """移动前检查"""
        if self.ndb.in_combat:
            self.msg("战斗中无法移动！")
            return False
        
        if getattr(self.ndb, 'is_cultivating', False):
            self.msg("请先停止修炼。")
            return False
        
        return True
    
    def at_object_receive(self, moved_obj, source_location, **kwargs):
        """接收物品"""
        pass
    
    def return_appearance(self, looker, **kwargs):
        """外观描述"""
        text = super().return_appearance(looker, **kwargs)
        
        realm = getattr(self.ndb, 'realm', '未知')
        level = getattr(self.ndb, 'level', 1)
        
        text += f"\n境界: |c{realm}|n  等级: |y{level}|n"
        
        if self.ndb.in_combat:
            text += f"\n|r【战斗中】|n"
        
        return text