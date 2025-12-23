"""
commands/inventory.py
背包与装备命令集 - 最终精修版 (0错误/中文适配/别名支持)
"""
from evennia import Command, CmdSet
from world.loaders.game_data import get_config

class CmdInventory(Command):
    """
    查看背包
    用法: i, inventory
    """
    key = "inventory"
    aliases = ["背包", "i", "inv"]
    locks = "cmd:all()"
    help_category = "常用"
    
    def func(self):
        character = self.caller
        if not hasattr(character, 'inventory'):
            self.caller.msg("|r系统错误: 背包未初始化。|n")
            return
        
        # 获取数据
        items = character.inventory.list_items()
        usage = character.inventory.get_usage()
        capacity = character.inventory.get_capacity()
        
        # 头部显示 (使用 |c 青色，清晰不刺眼)
        header = f"|c【我的背包】|n |w({usage}/{capacity})|n"
        
        # 分隔线 (使用 |x 灰色，低调)
        div_line = "|x" + "-" * 60 + "|n"
        
        if not items:
            self.caller.msg(header)
            self.caller.msg(div_line)
            self.caller.msg("  |x(背包是空的)|n")
            self.caller.msg(div_line)
            return
            
        self.caller.msg("|x" + "=" * 60 + "|n")
        self.caller.msg(header)
        self.caller.msg(div_line)
        
        # 1. 显示已装备
        if hasattr(character, 'equipment'):
            equipped = character.equipment.get_equipped()
            if equipped:
                self.caller.msg("|g[已装备]|n") # 绿色标题
                for slot, item in equipped.items():
                    if item:
                        # 格式: [主手] +5 玄铁重剑
                        self.caller.msg(f"  |x[{slot}]|n {item.get_display_name(character)}")
                self.caller.msg("")

        # 2. 显示背包内容
        # 读取配置 (注意：因为我们要改 YAML 缩进，所以这里还是读取 'game.inventory_categories')
        cat_map = get_config('game.inventory_categories', {})
        
        categories = {}
        for item in items:
            cat = item['category']
            if cat not in categories: categories[cat] = []
            categories[cat].append(item)
            
        for cat, item_list in categories.items():
            # 翻译分类
            cat_name = cat_map.get(cat, cat)
            self.caller.msg(f"|y[{cat_name}]|n") # 黄色标题，醒目
            
            for item in item_list:
                if item['storage'] == 'db':
                    # 唯一物品
                    obj = item['object']
                    all_aliases = obj.aliases.all()
                    short_aliases = [
                        a for a in all_aliases 
                        if a != obj.key and a != obj.db.item_key
                    ]
                    display_code = short_aliases[0] if short_aliases else obj.db.item_key
                    # 物品名白色，代码灰色
                    self.caller.msg(f"  {obj.get_display_name(character)} |x({display_code})|n")
                else:
                    # 堆叠物品
                    self.caller.msg(f"  {item['name']} x{item['count']} |x({item['key']})|n")
            self.caller.msg("")
            
        self.caller.msg("|x" + "=" * 60 + "|n")
        self.caller.msg("|x提示: 输入 'use <代码>' 使用，'equip <代码>' 装备|n")


class CmdEquip(Command):
    """
    穿戴装备
    用法: equip <物品代码>
    别名: wear, 装备, 穿
    """
    key = "equip"
    aliases = ["wear", "装备", "穿"]
    help_category = "物品"
    
    def func(self):
        if not self.args:
            self.caller.msg("你要装备什么？")
            return
        
        # 去掉空格，精确搜索
        target_name = self.args.strip()
        target = self.caller.search(target_name, candidates=self.caller.contents)
        if not target: 
            return
        
        # 基础校验
        if not hasattr(target, 'db') or not target.db.template:
             self.caller.msg("这不是一件装备。")
             return

        # 调用 Handler
        if hasattr(self.caller, 'equipment'):
            # 这里的 equip 方法返回 (bool, str)
            success, msg = self.caller.equipment.equip(target)
            if success:
                self.caller.msg(f"|g{msg}|n")
            else:
                self.caller.msg(f"|r{msg}|n")
        else:
            self.caller.msg("|r错误: 装备系统未加载。|n")


class CmdUnequip(Command):
    """
    卸下装备
    用法: unequip <槽位名>
    别名: remove, 卸下, 脱
    """
    key = "unequip"
    aliases = ["remove", "卸下", "脱"]
    help_category = "物品"
    
    def func(self):
        if not self.args:
            self.caller.msg("你要卸下什么？(输入槽位名，如 weapon, armor)")
            return
            
        slot = self.args.strip()
        
        if hasattr(self.caller, 'equipment'):
            success, msg = self.caller.equipment.unequip(slot)
            if success:
                self.caller.msg(f"|g{msg}|n")
            else:
                self.caller.msg(f"|r{msg}|n")


class CmdUse(Command):
    """
    使用物品
    用法: use <物品代码> [数量]
    """
    key = "use"
    aliases = ["使用", "吃"]
    help_category = "物品"
    
    def func(self):
        if not self.args:
            self.caller.msg("|r用法: use <物品名称> [数量]|n")
            return
        
        args = self.args.split()
        item_identifier = args[0]
        amount = 1
        
        if len(args) > 1:
            try:
                amount = int(args[1])
            except ValueError:
                self.caller.msg("|r数量必须是数字|n")
                return
        
        # 尝试调用物品系统
        try:
            from world.systems.item_system import ItemSystem
            sys = ItemSystem()
            # 简单的循环使用
            for _ in range(amount):
                if not sys.use_item(self.caller, item_identifier):
                    break
        except ImportError:
            self.caller.msg("|r系统错误: ItemSystem 未找到。|n")
        except Exception as e:
            self.caller.msg(f"|r使用失败: {e}|n")


class CmdDrop(Command):
    """
    丢弃物品
    用法: drop <物品代码> [数量]
    """
    key = "drop"
    aliases = ["丢弃", "扔"]
    help_category = "物品"
    
    def func(self):
        if not self.args:
            self.caller.msg("|r用法: drop <物品名称> [数量]|n")
            return
        
        args = self.args.split()
        item_key = args[0]
        amount = 1
        if len(args) > 1 and args[1].isdigit():
            amount = int(args[1])

        # 1. 优先检查堆叠物品 (性能更高)
        if self.caller.inventory.has(item_key, amount):
            if self.caller.inventory.remove(item_key, amount):
                self.caller.msg(f"|y你丢弃了 {item_key} x{amount}。|n")
                return
        
        # 2. 检查唯一物品对象
        target = self.caller.search(item_key, candidates=self.caller.contents)
        if target:
            if hasattr(target, 'db') and target.db.equipped:
                self.caller.msg("|r无法丢弃已装备的物品，请先卸下。|n")
                return
            
            name = target.key
            # 物理删除对象
            target.delete() 
            self.caller.msg(f"|y你丢弃了 {name}。|n")
        else:
            self.caller.msg(f"|r你身上没有 {item_key}。|n")


class CmdGive(Command):
    """
    给予物品
    用法: give <玩家> = <物品> [数量]
    """
    key = "give"
    aliases = ["给予", "赠送", "给"]
    help_category = "交互"
    
    def func(self):
        if not self.lhs or not self.rhs:
            self.caller.msg("|r用法: give <玩家> = <物品> [数量]|n")
            return
        
        # 搜索目标
        target = self.caller.search(self.lhs)
        if not target: return
        
        # 距离检查
        if target.location != self.caller.location:
            self.caller.msg("|r目标不在附近|n")
            return
        
        # 解析参数
        args = self.rhs.split()
        item_key = args[0]
        amount = 1
        if len(args) > 1 and args[1].isdigit():
            amount = int(args[1])
            
        # 1. 堆叠物品转移
        if self.caller.inventory.has(item_key, amount):
            if self.caller.inventory.transfer_to(target, item_key, amount):
                self.caller.msg(f"|g你给予了 {target.key} {item_key} x{amount}。|n")
                target.msg(f"|g{self.caller.key} 给予了你 {item_key} x{amount}。|n")
                return

        # 2. 唯一物品对象转移
        obj = self.caller.search(item_key, candidates=self.caller.contents)
        if obj:
            # 安全检查
            if hasattr(obj, 'db'):
                if obj.db.bound_to:
                    self.caller.msg("|r该物品已绑定，无法交易。|n")
                    return
                if obj.db.equipped:
                    self.caller.msg("|r无法交易已装备的物品。|n")
                    return
                
            # 移动对象
            obj.location = target
            self.caller.msg(f"|g你把 {obj.key} 给了 {target.key}。|n")
            target.msg(f"|g{self.caller.key} 给了你 {obj.key}。|n")
        else:
            self.caller.msg(f"|r你身上没有 {item_key}。|n")


class InventoryCmdSet(CmdSet):
    key = "InventoryCmdSet"
    priority = 1
    def at_cmdset_creation(self):
        self.add(CmdInventory)
        self.add(CmdEquip)
        self.add(CmdUnequip)
        self.add(CmdUse)
        self.add(CmdDrop)
        self.add(CmdGive)