# migratemagic命令帮助条目

def add_migratemagic_help():
    """添加migratemagic命令的帮助条目"""

    # 创建migratemagic帮助条目
    help_entry = {
        "key": "migratemagic",
        "entrytext": """
|y角色魔法属性迁移命令|n
|w用法:|n
migratemagic [角色名]
magicmigrate [角色名]
mm [角色名]
addmagic [角色名]

|w描述:|n
为角色添加魔法系统相关属性。如果不指定角色名，将为所有角色添加魔法属性。
如果指定角色名，将只为该角色添加魔法属性。

|w示例:|n
migratemagic          # 为所有角色添加魔法属性
migratemagic Tom      # 只为Tom添加魔法属性
magicmigrate Jerry    # 只为Jerry添加魔法属性
mm Alice             # 只为Alice添加魔法属性

|w默认属性值:|n
- 法力值: 100/100
- 魔法强度: 5
- 所有抗性: 0
- 已知法术: ["fireball"]

|w注意:|n
此命令需要管理员权限。
如果角色已有魔法属性，将保留原有值，不会覆盖。
""",
        "category": "魔法管理",
        "locks": "view:perm(admins)"
    }

    # 检查帮助条目是否已存在
    from evennia.help.models import HelpEntry
    from evennia.utils import create

    # 删除旧的帮助条目
    old_entries = HelpEntry.objects.filter(db_key="migratemagic")
    for entry in old_entries:
        entry.delete()

    # 创建新的帮助条目
    new_entry = create.create_help_entry(
        key=help_entry["key"],
        entrytext=help_entry["entrytext"],
        category=help_entry["category"],
        locks=help_entry["locks"]
    )
    print(f"已创建/更新帮助条目: {help_entry['key']}")

    return new_entry
