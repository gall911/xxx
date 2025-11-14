from evennia import Command
from typeclasses.spells.loader import load_spell_data
from typeclasses.spells.spell_base import Spell

class CmdCast(Command):
    """
    施放技能命令
    """
    key = "cast"
    locks = "cmd:all()"
    
    def func(self):
        """执行命令"""
        if not self.args:
            self.caller.msg("施放什么技能？")
            return
            
        # 解析技能键和目标
        args = self.args.strip().lower().split()
        spell_key = args[0] if args else ""
        
        # 如果技能键不包含点号，尝试匹配已学会的技能
        if '.' not in spell_key:
            matched_key = None
            if hasattr(self.caller.db, 'skills'):
                # 遍历已学会的技能，查找匹配的技能
                for learned_skill_key in self.caller.db.skills.keys():
                    if learned_skill_key.endswith('.' + spell_key) or \
                       learned_skill_key == spell_key:
                        matched_key = learned_skill_key
                        break
            
            if matched_key:
                spell_key = matched_key
            else:
                self.caller.msg("你没有学会这个技能。")
                return
        else:
            # 判断是否已学会
            if not hasattr(self.caller.db, 'skills') or spell_key not in self.caller.db.skills:
                self.caller.msg("你没有学会这个技能。")
                return
            
        # 加载 JSON 数据
        data = load_spell_data(spell_key)
        if not data:
            self.caller.msg("技能不存在。")
            return
            
        # 获取目标
        target = None
        # 检查是否有明确指定的目标参数
        args = self.args.strip().split()
        if len(args) > 1:
            # 尝试通过名称查找目标
            target_name = args[1]
            # 在房间中查找目标
            for obj in self.caller.location.contents:
                # 检查对象的key是否匹配
                if hasattr(obj, 'key') and obj.key.lower() == target_name.lower():
                    target = obj
                    break
                # 检查对象的别名是否匹配
                elif hasattr(obj, 'aliases') and target_name.lower() in [alias.lower() for alias in obj.aliases.all()]:
                    target = obj
                    break
        
        # 如果没有明确指定目标，使用默认目标
        if not target:
            target = self.caller.db.target if hasattr(self.caller.db, 'target') else None
            
        if not target:
            self.caller.msg("你没有指定目标。")
            return
            
        # 创建技能对象
        spell = Spell(self.caller, data)
        
        # 计算伤害
        skill_level = self.caller.db.skills[spell_key]["level"]
        dmg = data["damage"]["base"] + data["damage"]["per_level"] * (skill_level - 1)
        
        # 应用伤害
        if not hasattr(target.db, 'hp') or target.db.hp is None:
            target.db.hp = 100  # 默认HP为100
            
        target.db.hp -= dmg
        
        # 确保HP不会低于0
        if target.db.hp < 0:
            target.db.hp = 0
            
        # 发送消息
        self.caller.msg(f"你施放了{data['name']}，对{target.key}造成{dmg}点伤害。")
        target.msg(f"{self.caller.key}对你施放了{data['name']}，造成{dmg}点伤害。")
        
        # 如果目标HP为0，发送死亡消息
        if target.db.hp == 0:
            self.caller.msg(f"{target.key}被你击败了！")
            target.msg("你被击败了！")