from evennia import Command

class CmdHit(Command):
    key = "hit"

    def func(self):
        target = self.caller.search(self.args)
        # 如果没有找到目标或找到多个目标，search方法会自动显示错误信息并返回None
        if not target:
            return
            
        self.caller.db.target = target
        self.caller.db.auto_fight = True
        self.caller.msg(f"你开始攻击 {target.key}！")