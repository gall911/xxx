"""
commands/craft.py
合成命令集

命令：
- craft/合成: 合成物品
- recipes/配方: 查看配方列表
- merge/合并: 合并装备
"""
from evennia import Command
from world.systems.craft_system import CraftSystem
from typeclasses.objects import UniqueItem


class CmdCraft(Command):
    """
    合成物品
    
    用法:
      craft <配方ID>
      合成 <配方ID>
    
    示例:
      craft craft_basic_sword    - 合成铁剑
      合成 craft_jade_ring        - 合成玉戒
    """
    
    key = "craft"
    aliases = ["合成", "make"]
    locks = "cmd:all()"
    help_category = "合成"
    
    def func(self):
        if not self.args:
            self.caller.msg("|r用法: craft <配方ID>|n")
            self.caller.msg("|y使用 'recipes' 查看可用配方|n")
            return
        
        recipe_id = self.args.strip()
        craft_system = CraftSystem()
        
        # 检查是否可以合成
        can, reason, recipe = craft_system.can_craft(self.caller, recipe_id)
        
        if not can:
            self.caller.msg(f"|r无法合成: {reason}|n")
            return
        
        # 显示配方信息
        self.caller.msg(f"\n|c【合成: {recipe.get('name', recipe_id)}】|n")
        
        materials = recipe.get('materials', {})
        self.caller.msg("|y需要材料:|n")
        from world.loaders.game_data import GAME_DATA
        for item_key, amount in materials.items():
            template = GAME_DATA.get('items', {}).get(item_key, {})
            name = template.get('name', item_key)
            has = self.caller.inventory.get(item_key)
            color = "|g" if has >= amount else "|r"
            self.caller.msg(f"  {name}: {color}{has}/{amount}|n")
        
        # 确认合成
        self.caller.msg("\n|w确认合成? (输入 'yes' 确认)|n")
        
        def _confirm(caller, response):
            if response.strip().lower() in ['yes', 'y', '是', '确认']:
                success, msg, item = craft_system.craft_equipment(caller, recipe_id)
                if success:
                    caller.msg(f"|g{msg}|n")
                else:
                    caller.msg(f"|r{msg}|n")
            else:
                caller.msg("|y已取消合成|n")
        
        # 使用 Evennia 的输入处理
        self.caller.cmdset.add("evennia.contrib.utils.CmdGet")
        self.caller.msg("> ", newline=False)
        
        # 简化版：直接合成（跳过确认）
        success, msg, item = craft_system.craft_equipment(self.caller, recipe_id)
        if success:
            self.caller.msg(f"\n|g{msg}|n")
        else:
            self.caller.msg(f"\n|r{msg}|n")


class CmdRecipes(Command):
    """
    查看合成配方
    
    用法:
      recipes [类型]
      配方 [类型]
    
    类型:
      equipment    - 装备合成
      consumable   - 消耗品合成
      merge        - 装备合并
    
    示例:
      recipes               - 查看所有配方
      配方 equipment         - 只看装备配方
    """
    
    key = "recipes"
    aliases = ["配方", "formula"]
    locks = "cmd:all()"
    help_category = "合成"
    
    def func(self):
        craft_system = CraftSystem()
        
        # 过滤类型
        filter_type = self.args.strip() if self.args else None
        
        if filter_type:
            recipes = craft_system.get_recipes_by_type(filter_type)
        else:
            recipes = craft_system.recipes
        
        if not recipes:
            self.caller.msg("|y没有找到配方|n")
            return
        
        self.caller.msg("|c" + "=" * 60 + "|n")
        self.caller.msg("|c【合成配方】|n")
        self.caller.msg("|c" + "=" * 60 + "|n")
        
        from world.loaders.game_data import GAME_DATA
        
        for recipe_id, recipe in recipes.items():
            name = recipe.get('name', recipe_id)
            recipe_type = recipe.get('type', 'unknown')
            required_level = recipe.get('required_level', 0)
            
            # 检查是否可以合成
            can, _, _ = craft_system.can_craft(self.caller, recipe_id)
            status_color = "|g" if can else "|r"
            status_text = "✓" if can else "✗"
            
            self.caller.msg(f"\n{status_color}[{status_text}]|n |y{name}|n (ID: {recipe_id})")
            self.caller.msg(f"    类型: {recipe_type} | 需要等级: {required_level}")
            
            # 显示材料
            materials = recipe.get('materials', {})
            if materials:
                self.caller.msg("    材料:")
                for item_key, amount in materials.items():
                    template = GAME_DATA.get('items', {}).get(item_key, {})
                    item_name = template.get('name', item_key)
                    has = self.caller.inventory.get(item_key)
                    mat_color = "|g" if has >= amount else "|r"
                    self.caller.msg(f"      {item_name}: {mat_color}{has}/{amount}|n")
            
            # 显示结果
            result = recipe.get('result', {})
            result_item_key = result.get('item_key')
            if result_item_key:
                result_template = GAME_DATA.get('items', {}).get(result_item_key, {})
                result_name = result_template.get('name', result_item_key)
                self.caller.msg(f"    产出: |c{result_name}|n")
        
        self.caller.msg("\n|c" + "=" * 60 + "|n")
        self.caller.msg("|w提示: 使用 'craft <配方ID>' 进行合成|n")


class CmdMerge(Command):
    """
    合并装备
    
    用法:
      merge <配方ID>
      合并 <配方ID>
    
    示例:
      merge merge_jade_ring    - 合并两个玉戒
    
    说明:
      某些装备可以合并成更高级的版本
      合并时会继承最好的词条
    """
    
    key = "merge"
    aliases = ["合并", "combine"]
    locks = "cmd:all()"
    help_category = "合成"
    
    def func(self):
        if not self.args:
            self.caller.msg("|r用法: merge <配方ID>|n")
            self.caller.msg("|y使用 'recipes merge' 查看可合并的装备|n")
            return
        
        recipe_id = self.args.strip()
        craft_system = CraftSystem()
        
        recipe = craft_system.get_recipe(recipe_id)
        if not recipe or recipe.get('type') != 'equipment_merge':
            self.caller.msg("|r配方不存在或类型错误|n")
            return
        
        # 获取所需装备
        source_item_key = recipe.get('source_item')
        source_count = recipe.get('source_count', 2)
        
        # 查找背包中的装备
        source_items = []
        for obj in self.caller.contents:
            if isinstance(obj, UniqueItem) and obj.db.item_key == source_item_key:
                source_items.append(obj)
        
        if len(source_items) < source_count:
            from world.loaders.game_data import GAME_DATA
            template = GAME_DATA.get('items', {}).get(source_item_key, {})
            name = template.get('name', source_item_key)
            self.caller.msg(
                f"|r材料不足！需要 {source_count} 个 {name}，"
                f"当前只有 {len(source_items)} 个|n"
            )
            return
        
        # 选择要合并的装备
        selected = source_items[:source_count]
        
        # 显示信息
        self.caller.msg(f"\n|c【合并装备】|n")
        self.caller.msg(f"|y将要合并以下装备:|n")
        for i, item in enumerate(selected, 1):
            self.caller.msg(f"  {i}. {item.get_display_name(self.caller)}")
        
        # 显示材料需求
        materials = recipe.get('materials', {})
        if materials:
            self.caller.msg("\n|y额外材料:|n")
            from world.loaders.game_data import GAME_DATA
            for item_key, amount in materials.items():
                template = GAME_DATA.get('items', {}).get(item_key, {})
                name = template.get('name', item_key)
                has = self.caller.inventory.get(item_key)
                color = "|g" if has >= amount else "|r"
                self.caller.msg(f"  {name}: {color}{has}/{amount}|n")
        
        # 执行合并
        success, msg, new_item = craft_system.merge_equipment(
            self.caller,
            recipe_id,
            selected
        )
        
        if success:
            self.caller.msg(f"\n|g{msg}|n")
        else:
            self.caller.msg(f"\n|r{msg}|n")