物品与资源系统开发文档 (Item & Resource System)
版本: 1.0 (Final)
最后更新: 2025-12-08
1. 核心架构 (Architecture)
本项目采用 双轨制 (Hybrid System) 存储策略，旨在平衡数据库性能与游戏交互性。
分类	物品类型	存储方式	管理核心	适用场景
L1 资产	Asset	db.assets (字典)	AssetHandler	货币(金币/灵石)、基础材料(矿/皮)、积分。特点：无实体，极快。
L2 堆叠	Stackable	ObjectDB (数据库)	StackableObject	丹药、符箓、任务道具。特点：有实体，自动堆叠，可交易/拆分。
L3 独立	Equip	ObjectDB (数据库)	EquipHandler	武器、防具、法宝。特点：不可堆叠，有独立属性。
2. 数据配置 (Configuration)
所有物品定义均位于 data/items/base/ 目录下的 YAML 文件中（文件名不限，系统会自动加载）。
2.1 资产配置示例 (Asset)
只需定义 type: asset，系统会自动将其归入 AssetHandler 管理。
gold:
  type: asset
  name: 金币
  desc: 大陆通用货币。

iron_ore:
  type: asset
  name: 玄铁矿
  desc: 用于锻造的基础材料。
  2.2 堆叠物品示例 (Stackable)
定义 type: stackable。如果是消耗品，可以添加 effects 字段供 use 命令读取。
code
Yaml
pill_heal_01:
  type: stackable
  name: 回春丹
  desc: 一颗散发着草药清香的丹药。
  # 药效配置 (CmdUseItem 会读取这里)
  effects:
    action: heal        # 动作类型: heal, buff_atk 等
    value: 50           # 数值
3. 开发者接口 (API)
严禁直接操作 db 字段或手动 create_object。请统一使用以下接口，以确保系统稳定性。
3.1 统一发放物品 (最常用)
无论是发钱还是发药，统统调用这个函数。系统会自动判断是给数字还是给实体。
code
Python
from world.systems.item_system import give_item

# 发钱 (自动进 Asset 字典)
give_item(player, "gold", 100)

# 发药 (自动进背包并堆叠)
give_item(player, "pill_heal_01", 5)

# 发装备
give_item(player, "sword_iron", 1)
3.2 资产操作 (AssetHandler)
挂载在 character.asset_handler。
code
Python
# 查询数量
amount = player.asset_handler.get_amount("gold")

# 增加 (建议用 give_item，但手动加也可以)
player.asset_handler.add("gold", 100)

# 消耗 (返回 True 代表扣除成功，False 代表余额不足)
if player.asset_handler.consume("gold", 500):
    player.msg("购买成功！")
else:
    player.msg("钱不够！")
3.3 堆叠对象操作 (StackableObject)
实体对象 (obj) 的专用方法。
code
Python
obj = player.search("回春丹")

# 1. 拆分 (Split) - 用于交易或给予
# 从 obj 中拆出 5 个生成 new_obj
new_obj = obj.split(5) 

# 2. 合并 (Merge) - 用于拾取
# 将 obj2 吃掉合并进 obj1
obj1.merge_from(obj2)

# 3. 消耗 (Consume) - 用于使用
# 消耗 1 个，如果数量归零会自动删除对象
obj.consume(1)
4. 关键文件索引 (File Index)
请勿随意移动或重命名以下核心文件，否则会导致系统崩溃。
文件路径	作用	备注
data/items/base/*.yaml	数据源	所有物品的 ID、名字、类型定义。
world/loaders/data_loader.py	加载器	负责把 YAML 读取到 GAME_DATA。
world/systems/item_system.py	系统核心	包含 give_item 接口，系统的总闸。
typeclasses/objects.py	实体逻辑	定义了 StackableObject (拆分/合并逻辑)。
typeclasses/asset_handler.py	资产逻辑	管理 db.assets 字典的增删查改。
typeclasses/characters.py	挂载点	在 at_init 中初始化了 asset_handler。
commands/inventory.py	界面命令	包含 i (背包)、use (使用)、wear (穿戴)。
5. 常见维护场景 (FAQ)
Q1: 如何让背包里的属性名显示中文（如 Strength -> 臂力）？
A: 修改 data/attributes.yaml，并在 commands/inventory.py 中确认已调用 AttrManager.get_name(key)。
Q2: 为什么我加了新物品，游戏里 give 提示找不到？
A: 必须 重启服务器 (evennia reload)。因为 YAML 数据是在服务器启动时加载到内存的。
Q3: 如何修改背包显示的排版？
A: 编辑 commands/inventory.py 中的 func 方法。推荐使用 evennia.utils.utils.pad 来处理中文对齐。
Q4: 玩家的老号报错 AttributeError: has no attribute 'asset_handler'？
A: 这是因为老号没有初始化 Handler。
确保 typeclasses/characters.py 的 at_init 里有 self.asset_handler = AssetHandler(self)。
重启服务器 (reload)。
让该玩家重新登录，或者管理员执行 @py self.at_init()。