"""
施法延迟脚本类
用于处理技能施法时间的延迟效果
"""
from evennia.scripts.scripts import DefaultScript

class CastingDelayScript(DefaultScript):
    """
    施法延迟脚本类
    当玩家开始施放一个有施法时间的技能时，创建此脚本实例来处理延迟效果
    """
    
    def at_script_creation(self):
        """
        初始化脚本属性
        """
        self.key = "casting_delay"
        self.desc = "技能施法延迟"
        self.interval = 0  # 立即执行，不重复
        self.persistent = False  # 不持久化存储
        self.start_delay = True  # 延迟开始执行
        # 注意：不要在这里设置self.db属性，因为脚本还没有被保存到数据库
        
    def setup(self, caster, spell_key, spell_data, target):
        """
        设置脚本参数
        """
        # 先添加脚本到施法者，确保脚本被正确初始化并保存到数据库
        caster.scripts.add(self)
        
        # 设置基本属性
        self.db.caster = caster
        self.db.spell_key = spell_key
        self.db.spell_data = spell_data
        self.db.target = target
        self.db.spell_name = spell_data.get('name', '未知技能')
        
        # 设置延迟时间
        cast_time = spell_data.get("cast_time", 0)
        self.interval = cast_time
        self.repeats = 1  # 只执行一次
            
    def at_start(self):
        """
        脚本开始时调用
        通知玩家开始施法
        """
        if self.db.caster and self.db.spell_name:
            # 获取技能等级
            skill_level = 1
            if hasattr(self.db.caster.db, 'skills') and self.db.spell_key in self.db.caster.db.skills:
                skill_level = self.db.caster.db.skills[self.db.spell_key]["level"]
                
            # 显示详细的技能信息
            cast_time = self.db.spell_data.get("cast_time", 0)
            cooldown = self.db.spell_data.get("cooldown", 0)
            self.db.caster.msg(f"你开始施放{self.db.spell_name} (等级 {skill_level})...")
            self.db.caster.msg(f"  吟唱时间: {cast_time}秒  冷却时间: {cooldown}秒")
            
    def at_repeat(self):
        """
        定时间隔执行（在施法时间结束后调用）
        执行实际的技能效果
        """
        self.execute_spell()
        # 执行完技能后停止脚本
        self.stop()
        
    def at_stop(self):
        """
        脚本停止时调用
        """
        pass
        
    def execute_spell(self):
        """
        执行技能效果
        """
        if not self.db.caster or not self.db.spell_data or not self.db.target:
            return
            
        # 获取施法者技能等级
        skill_level = 1
        if hasattr(self.db.caster.db, 'skills') and self.db.spell_key in self.db.caster.db.skills:
            skill_level = self.db.caster.db.skills[self.db.spell_key]["level"]
            
        # 计算伤害
        data = self.db.spell_data
        # 修复伤害计算逻辑，使用正确的字段访问方式
        damage_data = data.get("damage", {})
        base_damage = damage_data.get("base", 0)
        per_level_damage = damage_data.get("per_level", 0)
        dmg = base_damage + per_level_damage * (skill_level - 1)
        
        # 应用伤害
        if not hasattr(self.db.target.db, 'hp') or self.db.target.db.hp is None:
            self.db.target.db.hp = 100  # 默认HP为100
            
        self.db.target.db.hp -= dmg
        
        # 确保HP不会低于0
        if self.db.target.db.hp < 0:
            self.db.target.db.hp = 0
            
        # 发送消息
        spell_name = data['name']
        self.db.caster.msg(f"你施放了{spell_name}，对{self.db.target.key}造成{dmg}点伤害。")
        self.db.target.msg(f"{self.db.caster.key}对你施放了{spell_name}，造成{dmg}点伤害。")
        
        # 如果目标HP为0，发送死亡消息
        if self.db.target.db.hp == 0:
            self.db.caster.msg(f"{self.db.target.key}被你击败了！")
            self.db.target.msg("你被击败了！")
            
        # 设置冷却时间
        cooldown = data.get("cooldown", 0)
        if cooldown > 0 and hasattr(self.db.caster, 'scripts'):
            from typeclasses.combat.engine import set_cooldown
            set_cooldown(self.db.caster, self.db.spell_key, cooldown)
            self.db.caster.msg(f"{spell_name}进入冷却，冷却时间：{cooldown}秒")