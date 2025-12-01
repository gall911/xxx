"""
战斗数据调试与修复工具
"""
from evennia import Command

class CmdCombatDebug(Command):
    """
    战斗数据诊断与修复
    
    用法:
      xx cbug <目标>       - 查看目标的战斗数据健康状况
      xx cbug/fix <目标>   - 强制修复目标的坏数据(None转为[])
      
    示例:
      xx cbug self
      xx cbug/fix NPC#1
    """
    
    key = "xx cbug"
    aliases = ["combatbug"]
    locks = "cmd:all()"
    help_category = "开发"
    
    def func(self):
        if not self.args:
            target = self.caller
        else:
            target = self.caller.search(self.args.strip())
            if not target:
                return
        
        # 1. 诊断模式
        if not self.switches:
            self._diagnose(target)
            return
            
        # 2. 修复模式
        if 'fix' in self.switches:
            self._fix_data(target)
            return

    def _diagnose(self, target):
        """诊断数据"""
        self.caller.msg(f"|w=== {target.key} 战斗数据诊断 ===|n")
        
        # 检查列表类型的属性
        list_attrs = ['skills', 'passive_skills']
        for attr in list_attrs:
            val = getattr(target.ndb, attr, "未定义")
            status = "|g正常|n"
            
            if val == "未定义":
                status = "|y缺失 (将被视为None)|n"
            elif val is None:
                status = "|r危险! (是None, 会导致崩溃)|n"
            elif not isinstance(val, list):
                status = f"|r错误类型 ({type(val)})|n"
            elif len(val) == 0:
                status = "|w空列表 (安全)|n"
            else:
                status = f"|g正常 (包含 {len(val)} 个)|n"
                
            self.caller.msg(f"Attribute '{attr}': {val} -> {status}")

        # 检查数值类型
        num_attrs = ['hp', 'max_hp', 'qi']
        for attr in num_attrs:
            val = getattr(target.ndb, attr, None)
            if isinstance(val, (int, float)):
                self.caller.msg(f"Attribute '{attr}': {val} |gOK|n")
            else:
                self.caller.msg(f"Attribute '{attr}': {val} |r异常 (非数字)|n")

        self.caller.msg("|w提示: 使用 xx cbug/fix <目标> 可自动修复|n")

    def _fix_data(self, target):
        """修复坏数据"""
        fixed_count = 0
        
        # 1. 修复列表 (None -> [])
        for attr in ['skills', 'passive_skills']:
            val = getattr(target.ndb, attr, None)
            if val is None or not isinstance(val, list):
                setattr(target.ndb, attr, [])
                self.caller.msg(f"|g已修复|n {attr}: None -> []")
                fixed_count += 1
                
        # 2. 修复数值
        if not isinstance(getattr(target.ndb, 'hp', None), (int, float)):
            target.ndb.hp = 100
            self.caller.msg(f"|g已修复|n hp -> 100")
            fixed_count += 1
            
        if not isinstance(getattr(target.ndb, 'max_hp', None), (int, float)):
            target.ndb.max_hp = 100
            self.caller.msg(f"|g已修复|n max_hp -> 100")
            fixed_count += 1

        if fixed_count > 0:
            self.caller.msg(f"|y共修复了 {fixed_count} 个数据问题。现在应该不会卡死了。|n")
        else:
            self.caller.msg("|g数据看起来很健康，无需修复。|n")