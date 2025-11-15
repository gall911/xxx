"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""

from evennia.objects.objects import DefaultCharacter

from .objects import ObjectParent


class Character(ObjectParent, DefaultCharacter):
    """
    The Character just re-implements some of the Object's methods and hooks
    to represent a Character entity in-game.

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Object child classes like this.

    """
    
    def at_hit(self, damage, attacker=None):
        """
        当角色受到攻击时调用此方法
        """
        # 减血逻辑...
        if hasattr(self.db, 'hp'):
            self.db.hp -= damage
        else:
            self.db.hp = 100 - damage  # 默认HP为100
            
        # 确保HP不会低于0
        if self.db.hp < 0:
            self.db.hp = 0
            
        # 中断施法（如果角色在吟唱）
        if hasattr(self.ndb, "casting") and getattr(self.ndb, "casting", None):
            self.ndb.casting = None
            self.location.msg_contents(f"{self.key} 的施法被打断！")
            
        # 如果HP为0，发送死亡消息
        if self.db.hp == 0:
            self.location.msg_contents(f"{self.key}被击败了！")