# commands/cultivation.py
"""修炼系统命令 - 修复版"""
from evennia import Command
from evennia import default_cmds


# ========== 🔥 修复: 使用 *args 捕获参数 ==========
def cultivate_tick(*args, **kwargs):
    """修炼Tick (独立函数)"""
    from evennia import search_object
    from world.loaders.game_data import get_data
    from world.systems.attr_manager import AttrManager
    from world.const import At
    
    # 🔥 从 args 或 kwargs 获取 character_id
    if args:
        character_id = args[0]
    elif 'character_id' in kwargs:
        character_id = kwargs['character_id']
    else:
        # 从 idstring 解析 (备用方案)
        idstring = kwargs.get('idstring', '')
        if 'cultivate_' in idstring:
            character_id = int(idstring.replace('cultivate_', ''))
        else:
            return
    
    chars = search_object(f"#{character_id}")
    if not chars:
        return
    
    character = chars[0]
    
    # 检查是否还在修炼
    if not getattr(character.ndb, 'is_cultivating', False):
        from evennia import TICKER_HANDLER
        TICKER_HANDLER.remove(
            interval=5,
            callback=cultivate_tick,
            idstring=f"cultivate_{character_id}"
        )
        return
    
    # 获取境界数据
    realm_name = getattr(character.ndb, 'realm', '练气期')
    realm_data = get_data('realms', realm_name)
    
    if not realm_data:
        return
    
    # 恢复灵力
    qi_regen = max(1, realm_data.get('base_stats', {}).get('max_qi', 100) // 100)
    old_qi = character.ndb.qi
    max_qi = character.ndb.max_qi
    new_qi = min(old_qi + qi_regen, max_qi)
    
    if new_qi != old_qi:
        AttrManager.set_attr(character, At.QI, new_qi)
        qi_gained = new_qi - old_qi
    else:
        qi_gained = 0
    
    # 恢复生命
    hp_regen = max(1, qi_regen // 2)
    old_hp = character.ndb.hp
    max_hp = character.ndb.max_hp
    new_hp = min(old_hp + hp_regen, max_hp)
    
    if new_hp != old_hp:
        AttrManager.set_attr(character, At.HP, new_hp)
        hp_gained = new_hp - old_hp
    else:
        hp_gained = 0
    
    if qi_gained > 0 or hp_gained > 0:
        msg = "|gCultivating...|n"
        if qi_gained > 0:
            msg += f" |c+{qi_gained} Qi|n"
        if hp_gained > 0:
            msg += f" |g+{hp_gained} HP|n"
        character.msg(msg)


class CmdCultivate(Command):
    """
    Start cultivating
    
    Usage:
      cultivate
    
    Enter meditation state, slowly restore Qi and HP.
    """
    
    key = "cultivate"
    aliases = ["meditate","xl"]
    locks = "cmd:all()"
    help_category = "Cultivation"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        # 检查是否在战斗中
        if hasattr(caller.ndb, 'in_combat') and caller.ndb.in_combat:
            caller.msg("Cannot cultivate in combat!")
            return
        
        # 检查是否已在修炼
        if hasattr(caller.ndb, 'is_cultivating') and caller.ndb.is_cultivating:
            caller.msg("You are already cultivating.")
            return
        
        # 开始修炼
        caller.ndb.is_cultivating = True
        
        from evennia import TICKER_HANDLER
        
        # 🔥 修复: 使用独立函数,传递 character_id
        TICKER_HANDLER.add(
            interval=5,
            callback=cultivate_tick,
            call_kw={'character_id': caller.id},  # 🔥 用 call_kw 传参
            idstring=f"cultivate_{caller.id}",
            persistent=False
        )
        
        caller.msg("|gYou sit down and begin cultivating...|n")
        caller.msg("(Type 'stopcultivate' to stop)")


class CmdStopCultivate(Command):
    """
    Stop cultivating
    
    Usage:
      stopcultivate
      stop
    """
    
    key = "stopcultivate"
    aliases = ["stop"]
    locks = "cmd:all()"
    help_category = "Cultivation"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        if not getattr(caller.ndb, 'is_cultivating', False):
            caller.msg("You are not cultivating.")
            return
        
        # 停止修炼
        caller.ndb.is_cultivating = False
        
        # 🔥 修复: 不要用 callback 参数删除
        from evennia import TICKER_HANDLER
        try:
            TICKER_HANDLER.remove(idstring=f"cultivate_{caller.id}")
        except Exception as e:
            # 如果删除失败,不影响游戏
            pass
        
        caller.msg("|yYou open your eyes and finish cultivating.|n")


class CmdRealm(Command):
    """
    View realm information
    
    Usage:
      realm
    
    Display current realm and breakthrough info.
    """
    
    key = "realm"
    locks = "cmd:all()"
    help_category = "Cultivation"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        from world.loaders.game_data import get_data
        from world.systems.cultivation_system import ProgressionManager
        
        realm_name = caller.db.realm or '练气期'
        realm_data = get_data('realms', realm_name)
        
        if not realm_data:
            caller.msg("Realm data error.")
            return
        
        caller.msg("|w" + "=" * 50)
        caller.msg(f"|cRealm: {realm_name}|n")
        caller.msg("|w" + "=" * 50)
        
        desc = realm_data.get('desc', 'No description')
        caller.msg(f"\n{desc}\n")
        
        # 当前等级与经验
        current_level = caller.db.level or 1
        current_exp = caller.db.exp or 0
        max_level = realm_data.get('max_level', 10)
        
        caller.msg(f"|yCurrent Level:|n {current_level}/{max_level}")
        
        if current_level < max_level:
            required_exp = ProgressionManager.get_exp_for_next_level(caller)
            exp_percent = (current_exp / required_exp * 100) if required_exp > 0 else 0
            caller.msg(f"|yExp:|n {current_exp}/{required_exp} ({exp_percent:.1f}%)")
        else:
            caller.msg("|yExp:|n Max level reached")
        
        # 属性加成
        base_stats = realm_data.get('base_stats', {})
        if base_stats:
            caller.msg("\n|gBase Stats:|n")
            from world.systems.attr_manager import AttrManager
            for attr, value in base_stats.items():
                attr_name = AttrManager.get_name(attr)
                caller.msg(f"  {attr_name}: {value}")
        
        # 突破信息
        next_realm = realm_data.get('next_realm')
        if next_realm:
            caller.msg(f"\n|cNext Realm:|n {next_realm}")
            if current_level >= max_level:
                caller.msg("|y💫 You can attempt breakthrough! Type 'breakthrough' for details.|n")
        else:
            caller.msg("\n|yYou have reached the maximum realm!|n")
        
        caller.msg("|w" + "=" * 50)


class CmdBreakthrough(Command):
    """
    Attempt realm breakthrough
    
    Usage:
      breakthrough
      breakthrough confirm
    """
    
    key = "breakthrough"
    aliases = ["bt"]
    locks = "cmd:all()"
    help_category = "Cultivation"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        from world.systems.cultivation_system import BreakthroughManager
        
        # 显示突破信息
        if not self.args or self.args.strip() not in ['confirm', 'yes']:
            info = BreakthroughManager.get_breakthrough_info(caller)
            caller.msg(info)
            caller.msg("\n|yType 'breakthrough confirm' to proceed.|n")
            return
        
        # 执行突破
        success, msg = BreakthroughManager.do_breakthrough(caller)
        caller.msg(msg)
        
        if success:
            caller.location.msg_contents(
                f"|y✨ {caller.key} has successfully broken through to {caller.db.realm}!|n",
                exclude=caller
            )


class CmdExp(Command):
    """
    View experience info
    
    Usage:
      exp
    """
    
    key = "exp"
    locks = "cmd:all()"
    help_category = "Cultivation"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        from world.systems.cultivation_system import ProgressionManager
        from world.loaders.game_data import get_data
        
        realm_name = caller.db.realm or '练气期'
        realm_data = get_data('realms', realm_name)
        
        if not realm_data:
            caller.msg("Realm data error.")
            return
        
        current_level = caller.db.level or 1
        current_exp = caller.db.exp or 0
        max_level = realm_data.get('max_level', 10)
        
        caller.msg("|c" + "=" * 40)
        caller.msg(f"Realm: {realm_name} | Level: {current_level}/{max_level}")
        caller.msg("|c" + "=" * 40)
        
        if current_level < max_level:
            required_exp = ProgressionManager.get_exp_for_next_level(caller)
            exp_percent = (current_exp / required_exp * 100) if required_exp > 0 else 0
            
            # 经验条
            bar_length = 30
            filled = int(bar_length * exp_percent / 100)
            bar = "|g" + "█" * filled + "|x" + "░" * (bar_length - filled) + "|n"
            
            caller.msg(f"\nCurrent Exp: {current_exp:,} / {required_exp:,}")
            caller.msg(f"Progress: {bar} {exp_percent:.1f}%")
        else:
            caller.msg(f"\nCurrent Exp: {current_exp:,}")
            caller.msg("|yMax level reached, you can attempt breakthrough!|n")
        
        caller.msg("|c" + "=" * 40)


class CmdAddExp(Command):
    """
    Add experience (Dev only)
    
    Usage:
      addexp <amount>
    """
    
    key = "addexp"
    locks = "cmd:perm(Developer)"
    help_category = "Development"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        if not self.args:
            caller.msg("Usage: addexp <amount>")
            return
        
        try:
            amount = int(self.args.strip())
        except ValueError:
            caller.msg("Experience must be an integer.")
            return
        
        if amount <= 0:
            caller.msg("Experience must be greater than 0.")
            return
        
        from world.systems.cultivation_system import ProgressionManager
        
        leveled_up, level_count = ProgressionManager.add_exp(caller, amount)
        
        if leveled_up:
            caller.msg(f"\n|gLeveled up {level_count} time(s)!|n")


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
        self.add(CmdExp())
        self.add(CmdAddExp())