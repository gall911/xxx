"""快捷命令"""
from evennia import Command

class CmdQuickInit(Command):
    """
    快速初始化角色为满状态
    
    用法:
      xx init [目标]
      
    示例:
      xx init          - 初始化自己
      xx init #5       - 初始化指定对象
    """
    
    key = "xx init"
    aliases = ["xxi"]
    locks = "cmd:all()"
    help_category = "开发"
    
    def func(self):
        if not self.args:
            target = self.caller
        else:
            target = self.caller.search(self.args.strip(), global_search=True)
            if not target:
                return
        
        # 满状态
        target.ndb.hp = 9999
        target.ndb.max_hp = 9999
        target.ndb.qi = 9999
        target.ndb.max_qi = 9999
        target.ndb.strength = 100
        target.ndb.agility = 100
        target.ndb.intelligence = 100
        target.ndb.level = 99
        target.ndb.realm = '金丹期'
        target.ndb.skills = ['普通攻击', '重击', '吸血术', '血祭']
        target.ndb.inventory = {
            '聚气丹': 99,
            '回春丹': 99,
            '筑基丹': 99
        }
        
        self.caller.msg(f"|g已初始化 {target.key} 为满级状态！|n")

class CmdQuickHeal(Command):
    """
    快速回满HP和QI
    
    用法:
      xx heal [目标]
    """
    
    key = "xx heal"
    aliases = ["xxh"]
    locks = "cmd:all()"
    help_category = "开发"
    
    def func(self):
        if not self.args:
            target = self.caller
        else:
            target = self.caller.search(self.args.strip(), global_search=True)
            if not target:
                return
        
        target.ndb.hp = target.ndb.max_hp
        target.ndb.qi = target.ndb.max_qi
        
        self.caller.msg(f"|g{target.key} HP和QI已回满！|n")
