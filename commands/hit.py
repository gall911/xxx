from evennia import Command

class CmdHit(Command):
    key = "hit"

    def func(self):
        target = self.caller.search(self.args)
        self.caller.db.target = target
        self.caller.db.auto_fight = True
        self.caller.msg(f"你开始攻击 {target.key}！")