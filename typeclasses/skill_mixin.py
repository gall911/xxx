"""
typeclasses/skill_mixin.py
技能系统逻辑分离模块
"""

from world.loaders.game_data import get_data

class SkillHandlerMixin:
    """
    这个类专门负责处理角色的技能逻辑。
    Character 类通过继承这个类来获得所有技能方法。
    """

   
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
        
        # 初始化learned_skills
        if not hasattr(self.db, 'learned_skills') or self.db.learned_skills is None:
            self.db.learned_skills = {}
        
        # 检查是否已学会
        if skill_key in self.db.learned_skills:
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
            if prereq_skill not in self.db.learned_skills:
                prereq_data = get_data('skills', prereq_skill)
                prereq_name = prereq_data.get('name', prereq_skill) if prereq_data else prereq_skill
                self.msg(f"|r需要先学会 {prereq_name}！|n")
                return False
        
        # 学会技能
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
        if skill_key in (self.db.skill_slots or {}).values():
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
        
        for slot_name, skill_key in (self.db.skill_slots or {}).items():
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
        
        skill_slots = getattr(self.db, 'skill_slots', None) or {}
        learned_skills = getattr(self.db, 'learned_skills', None) or {}
        
        for slot_name, skill_key in skill_slots.items():
            if skill_key:
                level = learned_skills.get(skill_key, 1)
                result[slot_name] = (skill_key, level)
        
        # 加上装备提供的技能
        equipment_slots = getattr(self.db, 'equipment_skill_slots', None) or {}
        for slot_name, skill_key in equipment_slots.items():
            if skill_key:
                level = 1  # 装备技能默认1级
                result[slot_name] = (skill_key, level)
        
        return result
    
    def get_active_skills(self):
        """
        获取所有可用的主动技能（用于战斗）
        ✅ 永远包含basic_attack作为后备
        
        Returns:
            list: [(skill_key, skill_level), ...]
        """
        result = []
        
        skill_slots = getattr(self.db, 'skill_slots', None) or {}
        learned_skills = getattr(self.db, 'learned_skills', None) or {}
        
        for slot_name, skill_key in skill_slots.items():
            if skill_key and slot_name.startswith('attack'):
                level = learned_skills.get(skill_key, 1)
                result.append((skill_key, level))
        
        # 加上装备技能
        equipment_slots = getattr(self.db, 'equipment_skill_slots', None) or {}
        for slot_name, skill_key in equipment_slots.items():
            if skill_key:
                result.append((skill_key, 1))
        
        # ========== 永远包含basic_attack（后备技能） ==========
        basic_level = learned_skills.get('basic_attack', 1)
        result.append(('basic_attack', basic_level))
        
        return result
    
    def _sync_to_old_skill_system(self):
        """同步到旧的技能系统（向后兼容）"""
        active_skills = [key for key, level in self.get_active_skills()]
        self.ndb.skills = active_skills if active_skills else ['basic_attack']