"""
typeclasses/characters.py
修复版 - 使用新的属性管理系统
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
        [新号出生] 只在角色第一次被创建时执行
        
        流程:
        1. 初始化属性结构 (attributes.yaml)
        2. 设定初始境界
        3. 应用境界基础属性 (realms.yaml)
        4. 应用等级成长
        5. 补满血蓝
        """
        super().at_object_creation()
        
        # 1. 初始化属性结构
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
        self.db.level = get_config('player.starting_level', 1)
        self.db.exp = 0
        
        # 5. 🔥 应用境界基础属性 (新API)
        AttrManager.apply_realm_stats(self)
        
        # 6. 🔥 应用等级成长 (新API)
        AttrManager.apply_level_growth(self)
        
        # 7. 🔥 补满血蓝
        max_hp = AttrManager.get_attr(self, At.MAX_HP)
        max_qi = AttrManager.get_attr(self, At.MAX_QI)
        AttrManager.set_attr(self, At.HP, max_hp)
        AttrManager.set_attr(self, At.QI, max_qi)
        
        # 8. 同步到内存并加载命令
        self.sync_stats_to_ndb()
        self._load_cmdsets()
        
        # 9. 新手礼包 (可选)
        self._give_starter_pack()

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
        
        # 4. 加载命令集 (不存数据库，防止膨胀)
        self._load_cmdsets()
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
        
        # 修复: 缺少属性
        if not self.attributes.has(At.HP):
            AttrManager.init_attributes(self)
            data_fixed = True
        
        # 修复: 缺少境界
        if not self.db.realm:
            self.db.realm = '练气期'
            self.db.level = 1
            self.db.exp = 0
            AttrManager.apply_realm_stats(self)
            AttrManager.apply_level_growth(self)
            data_fixed = True
        
        # 修复: 缺少等级/经验
        if self.db.level is None:
            self.db.level = 1
        if self.db.exp is None:
            self.db.exp = 0
        
        # 修复: 补全字典
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

        # === 清理旧的持久化命令集 (防止炸档) ===
        old_cmdsets = ["InventoryCmdSet", "CombatCmdSet", "CultivationCmdSet", "SkillCmdSet"]
        for cmdset_name in old_cmdsets:
            if self.cmdset.has(cmdset_name):
                try:
                    self.cmdset.delete(cmdset_name)
                except Exception:
                    pass

        # 欢迎消息
        self.msg(f"|g欢迎回来，{self.key}！|n")
        realm_name = getattr(self.ndb, 'realm', self.db.realm or '未知')
        level = self.db.level or 1
        self.msg(f"当前境界: {realm_name} (Lv.{level})")

    def at_post_unpuppet(self, account=None, session=None, **kwargs):
        """下线保存"""
        if hasattr(self, 'inventory'):
            self.inventory.force_save()
        super().at_post_unpuppet(account=account, session=session, **kwargs)

    def at_server_shutdown(self):
        """关机保存"""
        if hasattr(self, 'inventory'):
            self.inventory.force_save()
        super().at_server_shutdown()

    def sync_stats_to_ndb(self):
        """
        [核心机制] 硬盘 -> 内存 同步
        🔥 包含封顶逻辑，解决 1000/100 问题
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
        
        # 3. 🔥 计算 HP (封顶逻辑)
        db_max_hp = self.attributes.get(At.MAX_HP) or 100
        con_val = getattr(self.ndb, At.CONSTITUTION, 0)
        final_max_hp = db_max_hp + (con_val * 10) + equip_bonuses.get(At.MAX_HP, 0)
        setattr(self.ndb, At.MAX_HP, final_max_hp)
        
        current_hp = self.attributes.get(At.HP) or final_max_hp
        if current_hp > final_max_hp:
            current_hp = final_max_hp
            self.attributes.add(At.HP, current_hp)
        setattr(self.ndb, At.HP, current_hp)

        # 4. 🔥 计算 Qi (封顶逻辑)
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

    def _load_cmdsets(self):
        """加载命令集 (内存模式)"""
        try:
            from commands.combat import CombatCmdSet
            from commands.cultivation import CultivationCmdSet
            from commands.skill_commands import SkillCmdSet
            from commands.inventory import InventoryCmdSet
            
            # persistent=False 保证不写入数据库
            self.cmdset.add(CombatCmdSet, persistent=False)
            self.cmdset.add(CultivationCmdSet, persistent=False)
            self.cmdset.add(SkillCmdSet, persistent=False)
            self.cmdset.add(InventoryCmdSet, persistent=False)
        except Exception as e:
            print(f"命令集加载警告: {e}")

    def _load_dev_cmdset(self):
        """加载开发者命令集"""
        if self.id == 1 or self.is_superuser:
            try:
                from commands.dev.dev_cmdset import DevCmdSet
                self.cmdset.add(DevCmdSet, persistent=False)
            except Exception:
                pass

    def _give_starter_pack(self):
        """
        发放新手礼包
        
        从配置读取: player.starting_items
        """
        starting_items = get_config('player.starting_items', [])
        
        if not starting_items or not hasattr(self, 'give_item'):
            return
        
        for item_entry in starting_items:
            if isinstance(item_entry, dict):
                for item_key, amount in item_entry.items():
                    self.give_item(item_key, amount)
            elif isinstance(item_entry, str):
                # 格式: "物品名: 数量"
                if ':' in item_entry:
                    item_key, amount = item_entry.split(':')
                    self.give_item(item_key.strip(), int(amount.strip()))
    
    # ========== 便捷方法 ==========
    
    def return_appearance(self, looker, **kwargs):
        """查看状态面板"""
        text = super().return_appearance(looker, **kwargs)
        return text

    def give_item(self, item_key, amount=1):
        """添加物品 (便捷方法)"""
        if hasattr(self, 'inventory'):
            return self.inventory.add(item_key, amount)
        return False
    
    def take_item(self, item_key, amount=1):
        """移除物品 (便捷方法)"""
        if hasattr(self, 'inventory'):
            return self.inventory.remove(item_key, amount)
        return False
    
    def has_item(self, item_key, amount=1):
        """检查物品 (便捷方法)"""
        if hasattr(self, 'inventory'):
            return self.inventory.has(item_key, amount)
        return False