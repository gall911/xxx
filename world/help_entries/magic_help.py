
# 魔法系统帮助条目

def create_magic_help_entries():
    """
    创建魔法系统相关的帮助条目
    """

    # 魔法系统概述
    magic_overview = {
        "key": "魔法系统",
        "entrytext": """
        |y魔法系统概述|n

        魔法是这个世界中强大的力量来源，通过施放各种法术，你可以实现攻击、防御、治疗等多种效果。

        |w基本概念:|n
        - |c法术|n: 魔法的基本单位，每个法术都有特定的效果和消耗
        - |c法力值|n: 施放法术所需的能量，每个法术都会消耗一定法力
        - |c元素属性|n: 法术所属的元素类型，如火、水、土、风等
        - |c法术等级|n: 法术的强度等级，等级越高威力越大

        |w如何使用魔法:|n
        - 使用 |wcast <法术名> [at <目标>]|n 命令施放法术
        - 使用 |wspells|n 命令查看已学会的法术
        - 使用 |wspellinfo <法术名>|n 查看法术详细信息

        |w法术分类:|n
        - |c攻击法术|n: 用于对敌人造成伤害
        - |c防御法术|n: 用于保护自己或盟友
        - |c辅助法术|n: 用于提供各种增益效果
        - |c治疗法术|n: 用于恢复生命值

        |w元素抗性:|n
        每个角色都有各种元素的抗性，抗性越高，受到对应元素的伤害就越低。
        """,
        "category": "魔法",
        "locks": "view:all()"
    }

    # 施法命令帮助
    cast_help = {
        "key": "cast",
        "entrytext": """
        |y施法命令|n

        |w用法:|n
          cast <法术名> [at <目标>]
          cast <法术名> [on <目标>]

        |w示例:|n
          cast fireball at goblin
          cast fireball goblin
          cast fireball

        |w描述:|n
        使用此命令施放已学会的法术。如果没有指定目标，法术会随机选择房间内的一个目标。
        某些法术可能需要指定目标才能施放。

        |w注意:|n
        - 施放法术需要消耗法力值
        - 某些法术有冷却时间
        - 施法可能会被打断
        """,
        "category": "魔法",
        "locks": "view:all()"
    }

    # 法术列表命令帮助
    spells_help = {
        "key": "spells",
        "entrytext": """
        |y法术列表命令|n

        |w用法:|n
          spells
          法术

        |w描述:|n
        显示你已学会的所有法术列表，包括法术名称、描述和法力消耗。

        |w示例输出:|n
        |y你已学会的法术:|n
          |c火球术|n - 召唤一个炽热的火球攻击目标。(消耗: 10法力)
          |c水箭|n - 发射一支水箭攻击目标。(消耗: 8法力)
        """,
        "category": "魔法",
        "locks": "view:all()"
    }

    # 法术信息命令帮助
    spellinfo_help = {
        "key": "spellinfo",
        "entrytext": """
        |y法术信息命令|n

        |w用法:|n
          spellinfo <法术名>
          法术信息 <法术名>

        |w示例:|n
          spellinfo fireball

        |w描述:|n
        显示指定法术的详细信息，包括描述、法力消耗、伤害、元素属性等。

        |w示例输出:|n
        |y火球术|n
        |w描述:|n 召唤一个炽热的火球攻击目标。
        |w法力消耗:|n 10
        |w基础伤害:|n 20
        |w元素属性:|n fire
        |w法术等级:|n 1
        """,
        "category": "魔法",
        "locks": "view:all()"
    }

    # 魔法属性帮助
    magic_stats_help = {
        "key": "魔法属性",
        "entrytext": """
        |y魔法属性详解|n

        |w法力值 (Mana):|n
        - 施放法术所需的能量
        - 每个角色有最大法力值和当前法力值
        - 法力值会随时间缓慢恢复

        |w魔法强度 (Magic Power):|n
        - 影响法术的伤害效果
        - 魔法强度越高，法术伤害越大

        |w元素抗性 (Element Resistance):|n
        - 减少对应元素法术造成的伤害
        - 包括火、水、土、风、雷、冰、光、暗等元素
        - 抗性越高，受到的伤害越低

        |w法术冷却 (Spell Cooldown):|n
        - 某些法术施放后需要等待一段时间才能再次施放
        - 冷却时间因法术而异
        """,
        "category": "魔法",
        "locks": "view:all()"
    }

        # 管理员魔法命令帮助
    migratemagic_help = {
        "key": "migratemagic",
        "entrytext": """
        |y角色魔法属性迁移命令|n
        |w用法:|n
          migratemagic [角色名]
          
        |w描述:|n
        为角色添加魔法系统相关属性。如果不指定角色名，将为所有角色添加魔法属性。
        如果指定角色名，将只为该角色添加魔法属性。
        
        |w示例:|n
          migratemagic          # 为所有角色添加魔法属性
          migratemagic Tom      # 只为Tom添加魔法属性
        
        |w注意:|n
        此命令需要管理员权限。
        """,
        "category": "魔法管理",
        "locks": "view:perm(admins)"
    }
    
    reloadmagic_help = {
        "key": "reloadmagic",
        "entrytext": """
        |y重新加载魔法系统命令|n
        |w用法:|n
          reloadmagic
          
        |w描述:|n
        重新初始化魔法系统，重新注册所有法术。当你修改了法术定义或魔法系统核心逻辑后，
        可以使用此命令使更改生效，而无需重启服务器。
        
        |w注意:|n
        此命令需要管理员权限。
        """,
        "category": "魔法管理",
        "locks": "view:perm(admins)"
    }
    
    addspell_help = {
        "key": "addspell",
        "entrytext": """
        |y添加法术命令|n
        |w用法:|n
          addspell <角色名> = <法术名>
          
        |w描述:|n
        给指定角色添加一个法术。如果角色没有魔法系统属性，会自动为其添加。
        
        |w示例:|n
          addspell Tom = fireball
          addspell Jerry = water_arrow
        
        |w注意:|n
        此命令需要管理员权限。
        """,
        "category": "魔法管理",
        "locks": "view:perm(admins)"
    }
    
    removespell_help = {
        "key": "removespell",
        "entrytext": """
        |y移除法术命令|n
        |w用法:|n
          removespell <角色名> = <法术名>
          
        |w描述:|n
        从指定角色移除一个法术。
        
        |w示例:|n
          removespell Tom = fireball
          removespell Jerry = water_arrow
        
        |w注意:|n
        此命令需要管理员权限。
        """,
        "category": "魔法管理",
        "locks": "view:perm(admins)"
    }
    
    # 魔法管理概述
    magic_admin_overview = {
        "key": "魔法管理",
        "entrytext": """
        |y魔法系统管理概述|n
        魔法系统提供了一系列管理命令，帮助管理员维护和管理魔法系统。
        
        |w常用管理命令:|n
        - |cmigratemagic|n - 为角色添加魔法系统属性
        - |creloadmagic|n - 重新加载魔法系统
        - |caddspell|n - 给角色添加法术
        - |cremovespell|n - 从角色移除法术
        
        |w常见任务:|n
        1. |y为所有已有角色添加魔法属性|n
           使用命令: |wmigratemagic|n
           
        2. |y给特定角色添加新法术|n
           使用命令: |waddspell 角色名 = 法术名|n
           
        3. |y更新魔法系统后重新加载|n
           使用命令: |wreloadmagic|n
        
        |w注意:|n
        所有魔法管理命令都需要管理员权限才能使用。
        """,
        "category": "魔法管理",
        "locks": "view:perm(admins)"
    }
    
    # 魔法系统目录结构
    magic_structure_help = {
        "key": "魔法系统目录",
        "entrytext": """
        |y魔法系统目录结构|n
        |w魔法系统主目录:|n /home/gg/xxx/world/magic/
        |c__init__.py|n - 魔法系统初始化文件，包含系统启动代码
        |cmagic_system.py|n - 魔法系统核心脚本
        |cmigrate_characters.py|n - 角色数据迁移工具
        |cspells/|n - 法术定义目录
          |c__init__.py|n - 法术包初始化文件
          |cattack_spells/|n - 攻击法术目录
            |c__init__.py|n - 攻击法术包初始化文件
            |cfire_spells.py|n - 火系法术定义
          |cbase_spell.py|n - 基础法术类定义

        |w帮助条目目录:|n /home/gg/xxx/world/help_entries/
        |c__init__.py|n - 帮助条目包初始化文件
        |cmagic_help.py|n - 魔法系统帮助条目定义
        |cmigratemagic_help.py|n - 魔法迁移命令帮助条目

        |w如何添加新法术:|n
        1. |y确定法术类型和元素|n
           根据法术功能选择合适的目录，如攻击法术放在 attack_spells 目录下。
           根据元素属性创建对应的文件，如水系法术可创建 water_spells.py。

        2. |y创建法术类|n
           在相应文件中创建继承自 BaseSpell 的新法术类，例如：

           ```python
           class WaterArrow(BaseSpell):
               def at_object_creation(self):
                   super().at_object_creation()
                   self.db.name = "水箭术"
                   self.db.key = "water_arrow"
                   self.db.description = "发射一支水箭攻击目标。"
                   self.db.mana_cost = 8  # 法力消耗
                   self.db.damage = 15    # 基础伤害值
                   self.db.element = "water"  # 元素属性
                   self.db.level = 1       # 法术等级

               def cast(self, caster, target=None):
                   # 实现施法逻辑
                   # ...
                   return True, f"{caster.key}对{target.key}施放了水箭术！"
           ```

        3. |y实现法术效果|n
           在 cast 方法中实现法术的具体效果，包括:
           - 检查法力值是否足够
           - 计算伤害
           - 应用效果到目标
           - 返回结果消息

        4. |y更新帮助条目|n
           在 magic_help.py 中添加新法术的帮助信息。

        5. |y重新加载魔法系统|n
           使用 |wreloadmagic|n 命令使新法术生效，无需重启服务器。

        |w注意:|n
        - 所有法术类都必须继承自 BaseSpell
        - 确保法术的 key 属性是唯一的，这是系统识别法术的标识
        - 法术的元素属性会影响目标对应的元素抗性计算
        """,
        "category": "魔法",
        "locks": "view:all()"
    }

    return [magic_overview, cast_help, spells_help, spellinfo_help, magic_stats_help,
            migratemagic_help, reloadmagic_help, addspell_help, removespell_help,
            magic_admin_overview, magic_structure_help]
