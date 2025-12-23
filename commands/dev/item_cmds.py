# commands/dev/item_cmds.py
from evennia import Command
from evennia.utils import search
from world.systems.item_system import give_item

class CmdGiveItem(Command):
    """
    GM 发放物品/资源指令
    
    用法:
      give <玩家名> = <物品Key> [数量]
      
    示例:
      give 玩家A = gold 100
      give 玩家A = pill_heal_01 5
    """
    key = "give"
    aliases = ["xxgive", "xx give"]    
    locks = "cmd:perm(Builder)" # 只有 Builder 权限以上能用
    help_category = "Builder"

    def func(self):
        caller = self.caller
        
        if not self.args or "=" not in self.args:
            caller.msg("用法: give 玩家 = 物品Key [数量]")
            return

        # 解析参数: 玩家 = 物品Key 数量
        target_name, stuff = self.args.split("=", 1)
        target_name = target_name.strip()
        stuff = stuff.strip().split()
        
        if len(stuff) < 1:
            caller.msg("你需要指定物品Key。")
            return
            
        item_key = stuff[0]
        amount = 1
        if len(stuff) > 1:
            try:
                amount = int(stuff[1])
            except ValueError:
                caller.msg("数量必须是整数。")
                return

        # 1. 查找玩家
        target = caller.search(target_name)
        if not target:
            return

        # 2. 调用核心系统发货
        # 这一步会自动判断是 给钱(Asset) 还是 给药(Stackable)
        try:
            success = give_item(target, item_key, amount)
            if success:
                caller.msg(f"|g[系统] 已发放 {item_key} x{amount} 给 {target.key}。|n")
            else:
                caller.msg(f"|r[系统] 发放失败。请检查物品Key '{item_key}' 是否在 YAML 中定义。|n")
        except Exception as e:
            # 捕获潜在错误，防止游戏崩溃
            caller.msg(f"|r[异常] 代码报错: {e}|n")
            # 打印详细错误到控制台方便调试
            import traceback
            traceback.print_exc()