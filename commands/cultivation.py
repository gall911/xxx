# commands/cultivation.py
"""修炼系统命令"""
from evennia import Command
from evennia import default_cmds

class CmdCultivate(Command):
    """
    开始修炼
    
    用法:
      修炼
      cultivate
    
    进入打坐状态，缓慢恢复灵力和生命。
    """
    
    key = "修炼"
    aliases = ["cultivate", "meditate"]
    locks = "cmd:all()"
    help_category = "修炼"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        # 检查是否在战斗中
        if hasattr(caller.ndb, 'in_combat') and caller.ndb.in_combat:
            caller.msg("战斗中无法修炼！")
            return
        
        # 检查是否已在修炼
        if hasattr(caller.ndb, 'is_cultivating') and caller.ndb.is_cultivating:
            caller.msg("你已经在修炼中了。")
            return
        
        # 开始修炼
        caller.ndb.is_cultivating = True
        
        from evennia import TICKER_HANDLER
        
        # 每5秒恢复一次
        TICKER_HANDLER.add(
            interval=5,
            callback=self._cultivate_tick,
            idstring=f"cultivate_{caller.id}",
            persistent=False
        )
        
        caller.msg("|g你盘膝而坐，开始修炼...|n")
        caller.msg("(输入 '停止修炼' 结束)")
    
    def _cultivate_tick(self, *args, **kwargs):
        """修炼Tick"""
        # 从idstring获取角色ID
        idstring = kwargs.get('idstring', '')
        char_id = int(idstring.replace('cultivate_', ''))
        
        from evennia import search_object
        chars = search_object(f"#{char_id}")
        
        if not chars:
            return
        
        caller = chars[0]
        
        # 检查是否还在修炼
        if not getattr(caller.ndb, 'is_cultivating', False):
            from evennia import TICKER_HANDLER
            TICKER_HANDLER.remove(
                interval=5,
                callback=self._cultivate_tick,
                idstring=idstring
            )
            return
        
        from world.loaders.game_data import get_data
        
        # 获取境界数据
        realm_name = getattr(caller.ndb, 'realm', '练气期')
        realm_data = get_data('realms', realm_name)
        
        if not realm_data:
            return
        
        # 恢复灵力
        qi_regen = realm_data.get('qi_regen', 1)
        old_qi = caller.ndb.qi
        caller.ndb.qi = min(caller.ndb.qi + qi_regen, caller.ndb.max_qi)
        qi_gained = caller.ndb.qi - old_qi
        
        # 恢复生命（较慢）
        hp_regen = qi_regen // 2
        old_hp = caller.ndb.hp
        caller.ndb.hp = min(caller.ndb.hp + hp_regen, caller.ndb.max_hp)
        hp_gained = caller.ndb.hp - old_hp
        
        if qi_gained > 0 or hp_gained > 0:
            msg = "|g修炼中...|n"
            if qi_gained > 0:
                msg += f" |c+{qi_gained} 灵力|n"
            if hp_gained > 0:
                msg += f" |g+{hp_gained} 生命|n"
            caller.msg(msg)

class CmdStopCultivate(Command):
    """
    停止修炼
    
    用法:
      停止修炼
      stop
    """
    
    key = "停止修炼"
    aliases = ["stop", "stopcultivate"]
    locks = "cmd:all()"
    help_category = "修炼"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        if not getattr(caller.ndb, 'is_cultivating', False):
            caller.msg("你没有在修炼。")
            return
        
        # 停止修炼
        caller.ndb.is_cultivating = False
        
        from evennia import TICKER_HANDLER
        TICKER_HANDLER.remove(
            interval=5,
            callback=None,
            idstring=f"cultivate_{caller.id}"
        )
        
        caller.msg("|y你睁开双眼，结束了修炼。|n")

class CmdRealm(Command):
    """
    查看境界信息
    
    用法:
      境界
      realm
    
    显示当前境界和突破信息。
    """
    
    key = "境界"
    aliases = ["realm"]
    locks = "cmd:all()"
    help_category = "修炼"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        from world.loaders.game_data import get_data
        
        realm_name = getattr(caller.ndb, 'realm', '练气期')
        realm_data = get_data('realms', realm_name)
        
        if not realm_data:
            caller.msg("境界数据错误。")
            return
        
        caller.msg("|w" + "=" * 50)
        caller.msg(f"|c境界: {realm_name}|n")
        caller.msg("|w" + "=" * 50)
        
        desc = realm_data.get('desc', '无描述')
        caller.msg(f"\n{desc}\n")
        
        # 属性加成
        bonus = realm_data.get('attribute_bonus', {})
        if bonus:
            caller.msg("|y属性加成:|n")
            for attr, value in bonus.items():
                caller.msg(f"  {attr}: +{value}")
        
        # 解锁技能
        unlock_skills = realm_data.get('unlock_skills', [])
        if unlock_skills:
            caller.msg(f"\n|g解锁技能:|n {', '.join(unlock_skills)}")
        
        # 突破要求
        breakthrough = realm_data.get('breakthrough', {})
        if breakthrough:
            next_realm = breakthrough.get('next_realm')
            required_level = breakthrough.get('required_level', 0)
            required_items = breakthrough.get('required_items', [])
            
            caller.msg(f"\n|c突破到 {next_realm}:|n")
            caller.msg(f"  需要等级: {required_level}")
            if required_items:
                caller.msg(f"  需要物品: {', '.join(required_items)}")
        
        caller.msg("|w" + "=" * 50)

class CmdBreakthrough(Command):
    """
    尝试突破境界
    
    用法:
      突破
      breakthrough
    
    消耗突破丹药，尝试突破到下一境界。
    """
    
    key = "突破"
    aliases = ["breakthrough"]
    locks = "cmd:all()"
    help_category = "修炼"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        from world.loaders.game_data import get_data
        import random
        
        # 获取当前境界
        realm_name = getattr(caller.ndb, 'realm', '练气期')
        realm_data = get_data('realms', realm_name)
        
        if not realm_data:
            caller.msg("境界数据错误。")
            return
        
        breakthrough = realm_data.get('breakthrough')
        if not breakthrough:
            caller.msg("你已达到最高境界！")
            return
        
        # 检查等级要求
        required_level = breakthrough.get('required_level', 0)
        current_level = getattr(caller.ndb, 'level', 1)
        
        if current_level < required_level:
            caller.msg(f"等级不足！需要等级 {required_level}，当前 {current_level}")
            return
        
        # TODO: 检查是否有突破丹药
        required_items = breakthrough.get('required_items', [])
        
        # 简化版：直接突破（后期加物品系统）
        next_realm = breakthrough.get('next_realm')
        
        # 突破判定（这里简化为100%成功）
        success = True
        
        if success:
            # 突破成功
            caller.ndb.realm = next_realm
            
            # 应用新境界的属性加成
            next_realm_data = get_data('realms', next_realm)
            if next_realm_data:
                bonus = next_realm_data.get('attribute_bonus', {})
                for attr, value in bonus.items():
                    current = getattr(caller.ndb, attr, 0)
                    setattr(caller.ndb, attr, current + value)
                
                # 更新最大灵力
                new_max_qi = next_realm_data.get('max_qi', 100)
                caller.ndb.max_qi = new_max_qi
                caller.ndb.qi = new_max_qi  # 突破后满灵力
                
                # 解锁新技能
                unlock_skills = next_realm_data.get('unlock_skills', [])
                if unlock_skills:
                    if not hasattr(caller.ndb, 'skills'):
                        caller.ndb.skills = []
                    caller.ndb.skills.extend(unlock_skills)
            
            caller.msg("|y" + "=" * 50)
            caller.msg("|g【突破成功！】|n")
            caller.msg(f"|c恭喜你突破到 {next_realm}！|n")
            caller.msg("|y" + "=" * 50)
            
            # 显示变化
            if bonus:
                caller.msg("\n|g属性提升:|n")
                for attr, value in bonus.items():
                    caller.msg(f"  {attr}: +{value}")
            
            if unlock_skills:
                caller.msg(f"\n|g解锁技能:|n {', '.join(unlock_skills)}")
        else:
            caller.msg("|r【突破失败】|n")
            caller.msg("需要继续修炼...")

# 命令集
class CultivationCmdSet(default_cmds.CharacterCmdSet):
    """修炼命令集"""
    
    key = "CultivationCmdSet"
    
    def at_cmdset_creation(self):
        """添加命令到命令集"""
        super().at_cmdset_creation()
        
        self.add(CmdCultivate())
        self.add(CmdStopCultivate())
        self.add(CmdRealm())
        self.add(CmdBreakthrough())