"""
commands/dev/migrate_items.py
数据迁移脚本 - 将旧物品系统迁移到新系统

执行步骤：
1. reload  # 重载代码
2. migrate_items  # 执行迁移
3. @py from evennia import search_object; search_object(typeclass='typeclasses.objects.StackableObject')  # 验证
"""
from evennia import Command
from evennia.utils import search


class CmdMigrateItems(Command):
    """
    迁移旧物品系统到新系统
    
    用法:
      migrate_items          - 迁移所有角色的物品
      migrate_items preview  - 预览迁移（不执行）
      migrate_items cleanup  - 清理所有旧物品对象
    
    警告：
      此命令会删除所有StackableObject对象！
      请确保已备份数据库！
    """
    
    key = "migrate_items"
    locks = "cmd:perm(Developer)"
    help_category = "开发"
    
    def func(self):
        mode = self.args.strip() or "migrate"
        
        if mode == "preview":
            self._preview_migration()
        elif mode == "cleanup":
            self._cleanup_old_objects()
        elif mode == "migrate":
            self._execute_migration()
        else:
            self.caller.msg("|r未知模式，请使用: migrate_items [preview|cleanup|migrate]|n")
    
    def _preview_migration(self):
        """预览迁移（不执行）"""
        from typeclasses.objects import StackableObject
        from typeclasses.characters import Character
        
        self.caller.msg("|c" + "=" * 60)
        self.caller.msg("|c【迁移预览】")
        self.caller.msg("|c" + "=" * 60 + "|n")
        
        # 统计旧物品
        old_items = search.search_object(typeclass=StackableObject)
        self.caller.msg(f"\n|y找到 {len(old_items)} 个旧物品对象|n")
        
        # 按角色分组
        char_items = {}
        orphan_items = []
        
        for item in old_items:
            owner = item.location
            if owner and owner.is_typeclass(Character):
                if owner.key not in char_items:
                    char_items[owner.key] = []
                char_items[owner.key].append(item)
            else:
                orphan_items.append(item)
        
        # 显示统计
        self.caller.msg(f"\n|g角色持有: {len(char_items)} 个角色|n")
        for char_name, items in char_items.items():
            self.caller.msg(f"  {char_name}: {len(items)} 个物品")
            for item in items[:5]:  # 只显示前5个
                stack_id = item.db.stack_id or item.key
                count = item.db.stack_count or 1
                self.caller.msg(f"    - {item.key} (id:{stack_id}, x{count})")
            if len(items) > 5:
                self.caller.msg(f"    ... 还有 {len(items) - 5} 个")
        
        if orphan_items:
            self.caller.msg(f"\n|r孤立物品: {len(orphan_items)} 个（将被删除）|n")
            for item in orphan_items[:10]:
                self.caller.msg(f"  - {item.key} (#{item.id})")
        
        self.caller.msg("\n|y执行 'migrate_items' 开始迁移|n")
        self.caller.msg("|c" + "=" * 60 + "|n")
    
    def _execute_migration(self):
        """执行迁移"""
        from typeclasses.objects import StackableObject
        from typeclasses.characters import Character
        from typeclasses.inventory_handler import InventoryHandler
        
        self.caller.msg("|c" + "=" * 60)
        self.caller.msg("|c【开始迁移】")
        self.caller.msg("|c" + "=" * 60 + "|n")
        
        # 获取所有旧物品
        old_items = search.search_object(typeclass=StackableObject)
        self.caller.msg(f"\n|y找到 {len(old_items)} 个旧物品对象|n")
        
        if not old_items:
            self.caller.msg("|g没有需要迁移的物品|n")
            return
        
        # 按角色迁移
        migrated_count = 0
        deleted_count = 0
        error_count = 0
        
        for item in old_items:
            owner = item.location
            
            # 检查owner是否是角色
            if not owner or not owner.is_typeclass(Character):
                # 孤立物品，直接删除
                item.delete()
                deleted_count += 1
                continue
            
            try:
                # 确保角色有inventory
                if not hasattr(owner, 'inventory'):
                    owner.inventory = InventoryHandler(owner)
                
                # 提取物品信息
                item_key = item.db.stack_id or item.key
                count = item.db.stack_count or 1
                
                # 添加到新系统（使用item_key作为标识）
                # 注意：这里需要确保item_key在items.yaml中存在
                success = owner.inventory.add(item_key, count)
                
                if success:
                    # 删除旧对象
                    item.delete()
                    migrated_count += 1
                    self.caller.msg(f"|g✓ {owner.key}: {item.key} x{count} -> {item_key}|n")
                else:
                    # 如果item_key不在yaml中，尝试用key
                    success = owner.inventory.add(item.key, count)
                    if success:
                        item.delete()
                        migrated_count += 1
                        self.caller.msg(f"|y✓ {owner.key}: {item.key} x{count} (fallback)|n")
                    else:
                        error_count += 1
                        self.caller.msg(f"|r✗ {owner.key}: {item.key} 迁移失败（未找到配置）|n")
            
            except Exception as e:
                error_count += 1
                self.caller.msg(f"|r✗ {owner.key}: {item.key} 迁移出错: {e}|n")
        
        # 显示结果
        self.caller.msg("\n|c" + "=" * 60)
        self.caller.msg("|c【迁移完成】")
        self.caller.msg("|c" + "=" * 60 + "|n")
        self.caller.msg(f"|g成功迁移: {migrated_count} 个物品|n")
        self.caller.msg(f"|y删除孤立: {deleted_count} 个物品|n")
        if error_count > 0:
            self.caller.msg(f"|r迁移失败: {error_count} 个物品|n")
        
        self.caller.msg("\n|y建议执行 'migrate_items cleanup' 清理残留|n")
    
    def _cleanup_old_objects(self):
        """清理所有旧物品对象"""
        from typeclasses.objects import StackableObject, Equipment, Weapon, Armor
        
        self.caller.msg("|c" + "=" * 60)
        self.caller.msg("|c【清理旧对象】")
        self.caller.msg("|c" + "=" * 60 + "|n")
        
        # 统计
        total = 0
        
        # 清理StackableObject
        stackables = search.search_object(typeclass=StackableObject)
        for obj in stackables:
            obj.delete()
        total += len(stackables)
        self.caller.msg(f"|g清理 StackableObject: {len(stackables)} 个|n")
        
        # 清理Equipment（如果需要）
        equipments = search.search_object(typeclass=Equipment)
        for obj in equipments:
            obj.delete()
        total += len(equipments)
        self.caller.msg(f"|g清理 Equipment: {len(equipments)} 个|n")
        
        # 清理Weapon
        weapons = search.search_object(typeclass=Weapon)
        for obj in weapons:
            obj.delete()
        total += len(weapons)
        self.caller.msg(f"|g清理 Weapon: {len(weapons)} 个|n")
        
        # 清理Armor
        armors = search.search_object(typeclass=Armor)
        for obj in armors:
            obj.delete()
        total += len(armors)
        self.caller.msg(f"|g清理 Armor: {len(armors)} 个|n")
        
        self.caller.msg(f"\n|c总计清理: {total} 个对象|n")
        self.caller.msg("|c" + "=" * 60 + "|n")


class CmdTestInventory(Command):
    """
    测试新背包系统
    
    用法:
      test_inventory
    """
    
    key = "test_inventory"
    locks = "cmd:perm(Developer)"
    help_category = "开发"
    
    def func(self):
        character = self.caller
        
        self.caller.msg("|c" + "=" * 60)
        self.caller.msg("|c【背包系统测试】")
        self.caller.msg("|c" + "=" * 60 + "|n")
        
        # 测试1: 添加物品
        self.caller.msg("\n|y测试1: 添加物品|n")
        character.inventory.add('gold', 1000)
        self.caller.msg(f"  添加gold x1000")
        
        character.inventory.add('huichundan', 50)
        self.caller.msg(f"  添加huichundan x50")
        
        # 测试2: 查询物品
        self.caller.msg("\n|y测试2: 查询物品|n")
        gold = character.inventory.get('gold')
        pills = character.inventory.get('huichundan')
        self.caller.msg(f"  gold: {gold}")
        self.caller.msg(f"  huichundan: {pills}")
        
        # 测试3: 移除物品
        self.caller.msg("\n|y测试3: 移除物品|n")
        character.inventory.remove('gold', 100)
        self.caller.msg(f"  移除gold x100")
        gold = character.inventory.get('gold')
        self.caller.msg(f"  剩余gold: {gold}")
        
        # 测试4: 列出物品
        self.caller.msg("\n|y测试4: 列出物品|n")
        items = character.inventory.list_items()
        for item in items:
            self.caller.msg(f"  {item['name']} x{item['count']} [{item['storage']}]")
        
        # 测试5: 保存
        self.caller.msg("\n|y测试5: 强制保存|n")
        character.inventory.force_save()
        self.caller.msg(f"  已保存到数据库")
        
        self.caller.msg("\n|c" + "=" * 60)
        self.caller.msg("|g测试完成！|n")
        self.caller.msg("|c" + "=" * 60 + "|n")