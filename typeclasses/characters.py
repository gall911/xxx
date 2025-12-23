"""
typeclasses/characters.py
最终完整版 - 包含所有存档/读档/属性同步逻辑
移除了手动命令集加载，对接 default_cmdsets.py
"""
from evennia import DefaultCharacter
from world.loaders.game_data import get_config, get_data
from typeclasses.skill_mixin import SkillHandlerMixin
from world.systems.attr_manager import AttrManager
from world.const import At 

# 引入处理器
from typeclasses.equip_handler import EquipHandler 
from typeclasses.asset_handler import AssetHandler
from typeclasses.inventory_handler import InventoryHandler
from typeclasses.equipment_handler import EquipmentHandler


class Character(SkillHandlerMixin, DefaultCharacter):
    
    def at_object_creation(self):
        """
        [新号出生] 只在角色第一次被创建时执行。
        """
        super().at_object_creation()
        
        # 1. 初始化基础属性
        AttrManager.init_attributes(self)
        
        # 2. 初始化容器
        self.db.assets = {} 
        self.db.inventory_data = {} 
        self.db.equipment = {} 
        self.db.equipped = {} 
        
        # 3. 初始化技能槽
        self.db.learned_skills = {'basic_attack': 1}
        self.db.skill_slots = {
            'inner': None, 'movement': None, 'attack1': None, 'attack2': None
        }
        self.db.equipment_skill_slots = {
            'weapon_skill': None, 'armor_skill': None
        }
        
        # 4. 设定初始身份
        start_realm = get_config('player.starting_realm', '练气期')
        self.db.realm = start_realm
        self.db.level = 1
        self.db.exp = 0
        
        # 5. 应用境界数值
        self._apply_realm_bonuses()
        
        # 6. 补满状态
        if self.db.max_hp:
            self.db.hp = self.db.max_hp
        if self.db.max_qi:
            self.db.qi = self.db.max_qi
        
        # 7. 同步到内存
        # 注意：不再手动调用 _load_cmdsets，由 default_cmdsets.py 自动接管
        self.sync_stats_to_ndb()

    def at_init(self):
        """
        [系统启动] 每次服务器重启、重载时执行
        """
        super().at_init()
        
        # 1. 初始化纯内存属性
        if not hasattr(self.ndb, 'items'):
            self.ndb.items = {}
        
        self.ndb.in_combat = False
        self.ndb.combat_target = None
        self.ndb.buffs = []
        self.ndb.skill_cooldowns = {}
        
        # 2. 初始化处理器
        self.asset_handler = AssetHandler(self)
        self.inventory = InventoryHandler(self)
        self.equipment = EquipmentHandler(self)
        self.equip_handler = EquipHandler(self)  # 旧版兼容
        
        # 3. 同步属性到内存
        self.sync_stats_to_ndb()
        
        # 4. 加载开发命令集 (只给 ID=1 或 超级用户)
        self._load_dev_cmdset()
        
        # 5. 应用被动技能
        if hasattr(self, '_apply_equipped_passive_skills'):
            self._apply_equipped_passive_skills()

    def at_post_puppet(self, account=None, session=None, **kwargs):
        """
        [玩家登录] 数据检查与修复
        """
        super().at_post_puppet(account=account, session=session, **kwargs)
        
        # === 老号修复逻辑 ===
        data_fixed = False
        
        if not self.attributes.has(At.HP):
            AttrManager.init_attributes(self)
            data_fixed = True
            
        if not self.db.realm:
            self.db.realm = '练气期'
            self.db.level = 1
            self._apply_realm_bonuses()
            data_fixed = True
            
        # 补全字典
        for attr in ['equipment', 'equipped', 'assets', 'inventory_data']:
            if getattr(self.db, attr) is None:
                setattr(self.db, attr, {})
                data_fixed = True
        
        if data_fixed:
            # 重新初始化并同步
            self.asset_handler = AssetHandler(self)
            self.inventory = InventoryHandler(self)
            self.equipment = EquipmentHandler(self)
            self.sync_stats_to_ndb()
            self.msg("|y[系统] 角色数据已自动修复。|n")

        # === 🔥 关键修改 ===
        # 移除了所有清理命令集和手动加载命令集的代码。
        # 登录过程现在只负责显示信息。
        
        # 确保开发工具被加载（如果是管理员）
        self._load_dev_cmdset()

        self.msg(f"|g欢迎回来，{self.key}！|n")
        # 安全获取境界显示
        r_name = getattr(self.ndb, 'realm', '未知')
        r_lvl = getattr(self.ndb, 'level', 1)
        self.msg(f"当前境界: {r_name} (Lv.{r_lvl})")

    def at_post_unpuppet(self, account=None, session=None, **kwargs):
        """下线保存"""
        from world.loaders.game_data import get_config
        from world.systems.save_system import SaveSystem
        
        # 调用存档系统
        if get_config('game.save_system.save_on_logout', True):
            SaveSystem.save_character(self)
        
        # 强制保存背包
        if hasattr(self, 'inventory'):
            self.inventory.force_save()
            
        super().at_post_unpuppet(account=account, session=session, **kwargs)

    def at_server_shutdown(self):
        """关机保存"""
        # 触发属性回写
        if hasattr(self, '_save_to_db'):
            self._save_to_db()
        
        if hasattr(self, 'inventory'):
            self.inventory.force_save()
        super().at_server_shutdown()

    def sync_stats_to_ndb(self):
        """
        [核心机制] 硬盘 -> 内存 同步
        包含封顶逻辑，解决 1000/100 问题
        """
        # 1. 获取装备加成
        equip_bonuses = {}
        if hasattr(self, 'equipment'):
            equip_bonuses = self.equipment.get_total_stats()
        
        # 2. 同步基础四维
        combat_attrs = [
            At.STRENGTH, At.AGILITY, At.INTELLIGENCE, At.CONSTITUTION,
            At.CRITICAL_RATE, At.LUCK
        ]
        
        for attr in combat_attrs:
            base_val = self.attributes.get(attr) or 0
            bonus_val = equip_bonuses.get(attr, 0)
            setattr(self.ndb, attr, base_val + bonus_val)
        
        # 3. 计算 HP (封顶逻辑)
        # MaxHP = 基础 + 根骨加成 + 装备
        db_max_hp = self.attributes.get(At.MAX_HP) or 100
        con_val = getattr(self.ndb, At.CONSTITUTION, 0)
        final_max_hp = db_max_hp + (con_val * 10) + equip_bonuses.get(At.MAX_HP, 0)
        setattr(self.ndb, At.MAX_HP, final_max_hp)
        
        # CurrentHP 不能超过 MaxHP
        current_hp = self.attributes.get(At.HP) or final_max_hp
        if current_hp > final_max_hp:
            current_hp = final_max_hp
            self.attributes.add(At.HP, current_hp) # 写回修正后的值
        setattr(self.ndb, At.HP, current_hp)

        # 4. 计算 Qi (封顶逻辑)
        db_max_qi = self.attributes.get(At.MAX_QI) or 100
        int_val = getattr(self.ndb, At.INTELLIGENCE, 0)
        final_max_qi = db_max_qi + (int_val * 5) + equip_bonuses.get(At.MAX_QI, 0)
        setattr(self.ndb, At.MAX_QI, final_max_qi)
        
        current_qi = self.attributes.get(At.QI) or final_max_qi
        if current_qi > final_max_qi:
            current_qi = final_max_qi
            self.attributes.add(At.QI, current_qi)
        setattr(self.ndb, At.QI, current_qi)
        
        # 5. 同步其他
        self.ndb.level = self.db.level or 1
        self.ndb.realm = self.db.realm or "练气期"
        self.ndb.exp = self.db.exp or 0
        
        # 触发一次 DB -> NDB 的完全加载
        self._load_from_db()

    # ========== 存档/读档核心逻辑 ==========
    # 这部分代码非常重要，绝对不能删

    def _load_from_db(self):
        """🔥 上线加载: db → ndb"""
        # 基础进度属性
        self.ndb.realm = self.db.realm or '练气期'
        self.ndb.level = self.db.level or 1
        self.ndb.exp = self.db.exp or 0
        
        # 获取基础属性 (base)
        self.ndb.base_strength = self.attributes.get('strength') or 10
        self.ndb.base_agility = self.attributes.get('agility') or 10
        self.ndb.base_intelligence = self.attributes.get('intelligence') or 10
        self.ndb.base_constitution = self.attributes.get('constitution') or 10
        
        # 资源池基础值
        base_max_hp = self.attributes.get('max_hp') or 100
        base_max_qi = self.attributes.get('max_qi') or 100
        current_hp = self.attributes.get('hp') or base_max_hp
        current_qi = self.attributes.get('qi') or base_max_qi
        
        # 计算装备加成
        equip_bonus = {}
        if hasattr(self, 'equipment'):
            try:
                equip_bonus = self.equipment.get_total_stats()
            except:
                equip_bonus = {}
        
        # 合并: 总属性 = 基础 + 装备
        self.ndb.strength = self.ndb.base_strength + equip_bonus.get('strength', 0)
        self.ndb.agility = self.ndb.base_agility + equip_bonus.get('agility', 0)
        self.ndb.intelligence = self.ndb.base_intelligence + equip_bonus.get('intelligence', 0)
        self.ndb.constitution = self.ndb.base_constitution + equip_bonus.get('constitution', 0)
        
        # MaxHP/MaxQi 加装备
        final_max_hp = base_max_hp + equip_bonus.get('max_hp', 0)
        final_max_qi = base_max_qi + equip_bonus.get('max_qi', 0)
        
        self.ndb.max_hp = final_max_hp
        self.ndb.max_qi = final_max_qi
        
        # 当前值封顶 (显示用)
        self.ndb.hp = min(current_hp, final_max_hp)
        self.ndb.qi = min(current_qi, final_max_qi)
        
        # 其他属性
        self.ndb.critical_rate = self.attributes.get('critical_rate') or 0.05
        self.ndb.luck = self.attributes.get('luck') or 1

    def _save_to_db(self):
        """🔥 下线保存: ndb → db"""
        # 基础进度属性
        self.db.realm = self.ndb.realm
        self.db.level = self.ndb.level
        self.db.exp = self.ndb.exp
        
        # 🔥 四维属性: 保存 base_*
        # 注意：我们只保存 base 值，不保存加了装备后的总值，防止属性无限膨胀
        if hasattr(self.ndb, 'base_strength'):
            self.attributes.add('strength', self.ndb.base_strength)
        if hasattr(self.ndb, 'base_agility'):
            self.attributes.add('agility', self.ndb.base_agility)
        if hasattr(self.ndb, 'base_intelligence'):
            self.attributes.add('intelligence', self.ndb.base_intelligence)
        if hasattr(self.ndb, 'base_constitution'):
            self.attributes.add('constitution', self.ndb.base_constitution)
        
        # 🔥 资源池
        equip_bonus = {}
        if hasattr(self, 'equipment'):
            try:
                equip_bonus = self.equipment.get_total_stats()
            except:
                pass
        
        # 还原基础上限 = 当前总上限 - 装备加成
        base_max_hp = self.ndb.max_hp - equip_bonus.get('max_hp', 0)
        base_max_qi = self.ndb.max_qi - equip_bonus.get('max_qi', 0)
        
        # 当前值不能超过基础上限
        current_hp = min(self.ndb.hp, base_max_hp + equip_bonus.get('max_hp', 0))
        current_qi = min(self.ndb.qi, base_max_qi + equip_bonus.get('max_qi', 0))
        
        # 写入数据库
        self.attributes.add('hp', max(0, current_hp))
        self.attributes.add('qi', max(0, current_qi))
        self.attributes.add('max_hp', max(1, base_max_hp))
        self.attributes.add('max_qi', max(1, base_max_qi))
        
        # 其他属性
        if hasattr(self.ndb, 'critical_rate'):
            self.attributes.add('critical_rate', self.ndb.critical_rate)
        if hasattr(self.ndb, 'luck'):
            self.attributes.add('luck', self.ndb.luck)

    # ========== 辅助方法 ==========

    def _load_dev_cmdset(self):
        if self.id == 1 or self.is_superuser:
            try:
                from commands.dev.dev_cmdset import DevCmdSet
                self.cmdset.add(DevCmdSet, persistent=False)
            except Exception:
                pass

    def _apply_realm_bonuses(self):
        """应用境界数值 (权威来源)"""
        realm_name = self.db.realm
        realm_data = get_data('realms', realm_name)
        if not realm_data: return
        
        # 兼容 base_stats 写法
        stats = realm_data.get('base_stats', realm_data.get('attribute_bonus', {}))

        # 覆盖基础属性
        for key, value in stats.items():
            # 只有当属性在 attributes.yaml 里定义过才写入
            if self.attributes.has(key) or key in [At.MAX_HP, At.MAX_QI]:
                self.attributes.add(key, value)
        
    def return_appearance(self, looker, **kwargs):
        """查看状态面板"""
        text = super().return_appearance(looker, **kwargs)
        # 这里可以使用 CmdStatus 类似的排版，或者保持简单
        return text

    def give_item(self, item_key, amount=1):
        if hasattr(self, 'inventory'):
            return self.inventory.add(item_key, amount)
        return False
    
    def take_item(self, item_key, amount=1):
        if hasattr(self, 'inventory'):
            return self.inventory.remove(item_key, amount)
        return False
    
    def has_item(self, item_key, amount=1):
        if hasattr(self, 'inventory'):
            return self.inventory.has(item_key, amount)
        return False