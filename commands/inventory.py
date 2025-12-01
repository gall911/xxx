# commands/inventory.py
"""物品和背包命令"""
from evennia import Command
from evennia import default_cmds

class CmdInventory(Command):
    """
    查看背包
    
    用法:
      背包
      inventory
      i
    
    显示你的物品列表。
    """
    
    key = "背包"
    aliases = ["inventory", "inv", "i"]
    locks = "cmd:all()"
    help_category = "物品"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        # 获取背包（简化版：存在ndb）
        inventory = getattr(caller.ndb, 'inventory', {})
        
        if not inventory:
            caller.msg("你的背包是空的。")
            return
        
        caller.msg("|w" + "=" * 50)
        caller.msg("|c背包|n")
        caller.msg("|w" + "=" * 50)
        
        from world.loaders.game_data import get_data
        
        for item_id, count in inventory.items():
            item_data = get_data('items', item_id)
            if not item_data:
                continue
            
            name = item_data.get('name', item_id)
            desc = item_data.get('desc', '')
            
            caller.msg(f"\n|y{name}|n x{count}")
            if desc:
                caller.msg(f"  {desc}")
        
        caller.msg("|w" + "=" * 50)

class CmdUseItem(Command):
    """
    使用物品
    
    用法:
      使用 <物品名>
      use <item>
    
    使用背包中的消耗品。
    """
    
    key = "使用"
    aliases = ["use"]
    locks = "cmd:all()"
    help_category = "物品"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        if not self.args:
            caller.msg("使用什么物品？用法: 使用 <物品名>")
            return
        
        item_name = self.args.strip()
        
        # 查找物品
        from world.loaders.game_data import GAME_DATA, get_data
        
        item_id = None
        for iid, item_data in GAME_DATA['items'].items():
            if item_data.get('name') == item_name or iid == item_name:
                item_id = iid
                break
        
        if not item_id:
            caller.msg(f"找不到物品: {item_name}")
            return
        
        # 检查背包
        inventory = getattr(caller.ndb, 'inventory', {})
        
        if item_id not in inventory or inventory[item_id] <= 0:
            caller.msg(f"你没有 {item_name}。")
            return
        
        item_data = get_data('items', item_id)
        
        # 应用效果
        effects = item_data.get('effects', {})
        
        # 恢复生命
        if 'restore_hp' in effects:
            hp_restore = effects['restore_hp']
            old_hp = caller.ndb.hp
            caller.ndb.hp = min(caller.ndb.hp + hp_restore, caller.ndb.max_hp)
            actual = caller.ndb.hp - old_hp
            caller.msg(f"|g恢复了 {actual} 点生命！|n")
        
        # 恢复灵力
        if 'restore_qi' in effects:
            qi_restore = effects['restore_qi']
            old_qi = caller.ndb.qi
            caller.ndb.qi = min(caller.ndb.qi + qi_restore, caller.ndb.max_qi)
            actual = caller.ndb.qi - old_qi
            caller.msg(f"|c恢复了 {actual} 点灵力！|n")
        
        # 突破几率
        if 'breakthrough_chance' in effects:
            import random
            chance = effects['breakthrough_chance']
            if random.random() < chance:
                caller.msg("|y你感到体内灵力涌动，似乎可以尝试突破了！|n")
                caller.msg("(使用 '突破' 命令)")
            else:
                caller.msg("|r突破失败，继续努力吧。|n")
        
        # 消耗物品
        inventory[item_id] -= 1
        if inventory[item_id] <= 0:
            del inventory[item_id]
        
        caller.msg(f"使用了 {item_name}。")

class CmdSave(Command):
    """
    保存角色数据
    
    用法:
      保存
      save
    
    将当前的NDB数据保存到数据库。
    """
    
    key = "保存"
    aliases = ["save"]
    locks = "cmd:all()"
    help_category = "通用"
    
    def func(self):
        """执行命令"""
        caller = self.caller
        
        # 将ndb数据保存到db
        save_data = {
            'hp': getattr(caller.ndb, 'hp', 100),
            'max_hp': getattr(caller.ndb, 'max_hp', 100),
            'qi': getattr(caller.ndb, 'qi', 50),
            'max_qi': getattr(caller.ndb, 'max_qi', 50),
            'level': getattr(caller.ndb, 'level', 1),
            'exp': getattr(caller.ndb, 'exp', 0),
            'realm': getattr(caller.ndb, 'realm', '练气期'),
            'strength': getattr(caller.ndb, 'strength', 10),
            'agility': getattr(caller.ndb, 'agility', 10),
            'intelligence': getattr(caller.ndb, 'intelligence', 10),
            'skills': getattr(caller.ndb, 'skills', []),
            'inventory': getattr(caller.ndb, 'inventory', {}),
        }
        
        caller.db.character_data = save_data
        
        caller.msg("|g数据已保存！|n")

# 命令集
class InventoryCmdSet(default_cmds.CharacterCmdSet):
    """物品命令集"""
    
    key = "InventoryCmdSet"
    
    def at_cmdset_creation(self):
        """添加命令到命令集"""
        super().at_cmdset_creation()
        
        self.add(CmdInventory())
        self.add(CmdUseItem())
        self.add(CmdSave())