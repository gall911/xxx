"""
创建特殊NPC的命令
"""

from evennia import Command, create_object
from typeclasses.npc import NPC

class CmdCreateNPC(Command):
    """
    创建一个特殊NPC
    
    使用方法:
      create_npc <名字> [= invincible] [= english_name:<英文名>] [= display_name:<显示名称>]
      
    示例:
      create_npc 僵尸
      create_npc 僵尸 = invincible
      create_npc 僵尸 = english_name:zombie
      create_npc 僵尸 = display_name:木桩（mz）
      create_npc 僵尸 = invincible,english_name:zombie,display_name:无敌僵尸（zombie）
    """
    key = "create_npc"
    locks = "cmd:perm(Builders)"
    
    def func(self):
        """执行命令"""
        if not self.args:
            self.caller.msg("请提供NPC的名字。")
            return
            
        # 解析参数
        args = self.args.strip().split('=')
        npc_name = args[0].strip()
        is_invincible = False
        english_name = None
        display_name = None
        
        if len(args) > 1:
            options = args[1].strip().split(',')
            for option in options:
                option = option.strip()
                if option.lower() == 'invincible':
                    is_invincible = True
                elif option.startswith('english_name:') or option.startswith('英文名:'):
                    english_name = option.split(':')[1].strip()
                elif option.startswith('display_name:') or option.startswith('显示名称:'):
                    display_name = option.split(':', 1)[1].strip()
                    
        # 创建NPC
        try:
            # 获取当前位置
            location = self.caller.location
            
            # 创建NPC对象
            npc = create_object(NPC, key=npc_name, location=location)
            
            # 设置英文名（别名）
            if english_name:
                npc.aliases.add(english_name)
            
            # 设置显示名称
            if display_name:
                npc.db.display_name = display_name
            
            # 设置初始属性
            npc.db.hp = 100
            npc.db.max_hp = 100
            
            # 如果指定了无敌模式
            if is_invincible:
                npc.db.is_invincible = True
                
            # 发送成功消息
            self.caller.msg(f"成功创建NPC '{npc_name}'。")
            if display_name:
                self.caller.msg(f"显示名称设置为: {display_name}")
            if english_name:
                self.caller.msg(f"英文名设置为: {english_name}")
            if is_invincible:
                self.caller.msg("该NPC处于无敌模式。")
                
        except Exception as e:
            self.caller.msg(f"创建NPC时出错: {e}")