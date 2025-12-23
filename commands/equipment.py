"""
commands/equipment.py
装备命令集

命令：
- equip/装备: 穿戴装备
- unequip/卸下: 卸下装备
- equipped/已装备: 查看已装备
- enhance/强化: 强化装备
- repair/修理: 修理装备
"""
from evennia import Command
from typeclasses.objects import UniqueItem


class CmdEquip(Command):
    """
    穿戴装备
    
    用法:
      equip <装备名称>
      装备 <装备名称>
    
    示例:
      equip 玄铁重剑
      装备 铁剑
    """
    
    key = "equip"
    aliases = ["装备", "wear"]
    locks = "cmd:all()"
    help_category = "装备"
    
    def func(self):
        if not self.args:
            self.caller.msg("|r用法: equip <装备名称>|n")
            return
        
        # 查找装备
        item_name = self.args.strip()
        items = [obj for obj in self.caller.contents if isinstance(obj, UniqueItem)]
        
        target_item = None
        for item in items:
            if item_name.lower() in item.key.lower():
                target_item = item
                break
        
        if not target_item:
            self.caller.msg(f"|r找不到装备: {item_name}|n")
            return
        
        # 穿戴装备
        success, msg = self.caller.equipment.equip(target_item)
        
        if success:
            self.caller.msg(f"|g{msg}|n")
        else:
            self.caller.msg(f"|r{msg}|n")


class CmdUnequip(Command):
    """
    卸下装备
    
    用法:
      unequip <槽位或装备名称>
      卸下 <槽位或装备名称>
    
    示例:
      unequip main_hand    - 卸下主手装备
      卸下 玄铁重剑        - 卸下指定装备
      unequip all          - 卸下所有装备
    """
    
    key = "unequip"
    aliases = ["卸下", "remove"]
    locks = "cmd:all()"
    help_category = "装备"
    
    def func(self):
        if not self.args:
            self.caller.msg("|r用法: unequip <槽位|装备名|all>|n")
            return
        
        arg = self.args.strip().lower()
        
        # 卸下所有装备
        if arg == "all":
            count = self.caller.equipment.unequip_all()
            self.caller.msg(f"|g卸下了 {count} 件装备|n")
            return
        
        # 尝试按槽位卸下
        success, msg = self.caller.equipment.unequip(arg)
        
        if success:
            self.caller.msg(f"|g{msg}|n")
            return
        
        # 尝试按名称查找并卸下
        equipped = self.caller.equipment.get_equipped()
        for slot, item in equipped.items():
            if arg in item.key.lower():
                success, msg = self.caller.equipment.unequip(slot)
                if success:
                    self.caller.msg(f"|g{msg}|n")
                else:
                    self.caller.msg(f"|r{msg}|n")
                return
        
        self.caller.msg(f"|r找不到装备: {arg}|n")


class CmdEquipped(Command):
    """
    查看已装备
    
    用法:
      equipped
      已装备
      eq
    """
    
    key = "equipped"
    aliases = ["已装备", "eq"]
    locks = "cmd:all()"
    help_category = "装备"
    
    def func(self):
        equipped_list = self.caller.equipment.list_equipped()
        
        self.caller.msg("|c" + "=" * 60 + "|n")
        self.caller.msg("|c【已装备】|n")
        self.caller.msg("|c" + "=" * 60 + "|n")
        
        has_equipment = False
        
        for entry in equipped_list:
            slot_name = entry['slot_name']
            item = entry['item']
            
            if item:
                has_equipment = True
                display_name = item.get_display_name(self.caller)
                
                # 显示基本信息
                self.caller.msg(f"\n|y{slot_name}|n: {display_name}")
                
                # 显示属性
                stats = entry['stats']
                if stats:
                    stat_parts = []
                    for key, value in stats.items():
                        if key != 'durability':
                            stat_parts.append(f"{key}+{value}")
                    if stat_parts:
                        self.caller.msg(f"  属性: {', '.join(stat_parts)}")
                
                # 显示耐久度
                dur = item.db.durability
                max_dur = item.db.template.get('base_stats', {}).get('durability', 100)
                dur_color = "|r" if dur < 30 else "|y" if dur < 60 else "|g"
                self.caller.msg(f"  耐久: {dur_color}{dur}/{max_dur}|n")
                
                # 显示词条
                affixes = item.db.affixes or []
                if affixes:
                    from world.systems.affix_system import AffixSystem
                    affix_sys = AffixSystem()
                    affix_desc = affix_sys.get_affix_description(affixes)
                    self.caller.msg(f"\n{affix_desc}")
        
        if not has_equipment:
            self.caller.msg("\n|y未装备任何装备|n")
        
        # 显示总属性
        total_stats = self.caller.equipment.get_total_stats()
        if total_stats:
            self.caller.msg("\n|w【总属性加成】|n")
            for key, value in total_stats.items():
                self.caller.msg(f"  {key}: +{value}")
        
        self.caller.msg("|c" + "=" * 60 + "|n")


class CmdEnhance(Command):
    """
    强化装备
    
    用法:
      enhance <装备名称>
      强化 <装备名称>
    
    示例:
      enhance 玄铁重剑
      强化 铁剑
    """
    
    key = "enhance"
    aliases = ["强化", "upgrade"]
    locks = "cmd:all()"
    help_category = "装备"
    
    def func(self):
        if not self.args:
            self.caller.msg("|r用法: enhance <装备名称>|n")
            self.caller.msg("|y提示: 可以强化背包或已装备的装备|n")
            return
        
        item_name = self.args.strip()
        
        # 查找装备（背包+已装备）
        target_item = None
        
        # 1. 搜索背包
        for obj in self.caller.contents:
            if isinstance(obj, UniqueItem) and item_name.lower() in obj.key.lower():
                target_item = obj
                break
        
        # 2. 搜索已装备
        if not target_item:
            equipped = self.caller.equipment.get_equipped()
            for item in equipped.values():
                if item_name.lower() in item.key.lower():
                    target_item = item
                    break
        
        if not target_item:
            self.caller.msg(f"|r找不到装备: {item_name}|n")
            return
        
        # 调用强化逻辑
        success = target_item.enhance(success=True)  # 简化版，总是成功
        
        if success:
            self.caller.msg(f"|g强化成功！{target_item.key} 现在是 +{target_item.db.enhance_level}|n")
        else:
            self.caller.msg("|r强化失败|n")


class CmdRepair(Command):
    """
    修理装备
    
    用法:
      repair <装备名称> [数量]
      修理 <装备名称> [数量]
    
    示例:
      repair 玄铁重剑      - 修理10点耐久
      修理 铁剑 50         - 修理50点耐久
    """
    
    key = "repair"
    aliases = ["修理", "fix"]
    locks = "cmd:all()"
    help_category = "装备"
    
    def func(self):
        if not self.args:
            self.caller.msg("|r用法: repair <装备名称> [数量]|n")
            return
        
        args = self.args.split()
        item_name = args[0]
        amount = 10  # 默认修理10点
        
        if len(args) > 1:
            try:
                amount = int(args[1])
            except ValueError:
                self.caller.msg("|r数量必须是数字|n")
                return
        
        # 查找装备
        target_item = None
        
        for obj in self.caller.contents:
            if isinstance(obj, UniqueItem) and item_name.lower() in obj.key.lower():
                target_item = obj
                break
        
        if not target_item:
            equipped = self.caller.equipment.get_equipped()
            for item in equipped.values():
                if item_name.lower() in item.key.lower():
                    target_item = item
                    break
        
        if not target_item:
            self.caller.msg(f"|r找不到装备: {item_name}|n")
            return
        
        # 计算费用（示例：1金币修1点耐久）
        cost = amount
        
        if not self.caller.inventory.has('gold', cost):
            self.caller.msg(f"|r金币不足！需要 {cost} 金币|n")
            return
        
        # 扣除金币
        self.caller.inventory.remove('gold', cost)
        
        # 修理
        repaired = target_item.repair(amount)
        
        self.caller.msg(
            f"|g修理成功！{target_item.key} 恢复了 {repaired} 点耐久度|n"
            f"\n|w当前耐久: {target_item.db.durability}/100|n"
        )