"""
commands/npc_commands.py
NPC管理命令 - 智能配置版 (集成 AttrManager 和 技能系统)
"""
import os
import yaml
from evennia import Command, create_object, search_tag
from evennia.utils.evtable import EvTable
from evennia.utils.ansi import strip_ansi
from world.loaders.game_data import GAME_DATA 
from world.systems.attr_manager import AttrManager # <--- 关键引入
from world.const import At

BATCH_TAG_CATEGORY = "batch_code"

class CmdNPCBatch(Command):
    """
    全自动批量投放 NPC (xxbn)
    
    功能:
    1. 唯一怪 (unique: true) -> 存在则更新属性，不存在则创建。
    2. 普通怪 -> 直接投放 (如果需要清理旧怪，请配合清理命令)。
    3. 自动应用 AttrManager 和技能配置。
    
    用法:
      xxbn <文件名>
    """
    key = "xx batch npc"
    aliases = ["xxbn"]
    locks = "cmd:perm(Builder)"
    help_category = "开发"
    
    def func(self):
        if not self.args:
            self.caller.msg("用法: xxbn <文件名>")
            self._list_files()
            return
            
        filename = self.args.strip()
        if not filename.endswith('.yaml'): filename += ".yaml"
        file_path = os.path.join("data", "npcs", filename)
        
        if not os.path.exists(file_path):
            self.caller.msg(f"|r找不到文件:|n {file_path}")
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except Exception as e:
            self.caller.msg(f"|rYAML错误:|n {e}")
            return

        if not data: return
        
        # 统一解析数据格式
        npc_list = self._parse_yaml_data(data)
        self.caller.msg(f"|w识别到 {len(npc_list)} 个NPC配置...|n")
        
        cnt_create, cnt_update = 0, 0
        
        for config in npc_list:
            # 1. 获取基本信息
            key = config.get('key')
            name = config.get('name', key)
            is_unique = config.get('unique', False)
            loc_key = str(config.get('location', '')).strip()
            
            # 2. 定位房间
            location = self._find_room_unified(loc_key)
            if not location:
                self.caller.msg(f"|y[跳过]|n {name} -> 找不到房间 '{loc_key}'")
                continue
                
            # 3. 查找或创建 NPC
            npc = None
            
            # 如果是唯一怪，先搜索是否存在
            if is_unique:
                # 先按 Tag 找
                found = search_tag(key, category=BATCH_TAG_CATEGORY)
                # 再按房间里的名字找 (双保险)
                if not found:
                    found = [o for o in location.contents if o.key == key and o.is_typeclass("typeclasses.npcs.NPC")]
                
                if found:
                    npc = found[0]
                    self.caller.msg(f"|y[更新]|n {name}")
                    cnt_update += 1
            
            # 如果没找到，或者是普通怪，则创建
            if not npc:
                try:
                    # 区分 NPC 和 Monster (根据配置，默认 NPC)
                    typeclass = "typeclasses.npcs.NPC"
                    # 如果配置里有 type: monster，可以切换类 (未来扩展)
                    
                    npc = create_object(typeclass, key=key, location=location)
                    if is_unique:
                        npc.tags.add(key, category=BATCH_TAG_CATEGORY)
                    
                    self.caller.msg(f"|g[创建]|n {name} -> {location.key}")
                    cnt_create += 1
                except Exception as e:
                    self.caller.msg(f"|r创建失败 {key}: {e}|n")
                    continue
            
            # 4. 更新属性 (无论是新建的还是老怪，都刷一遍)
            self._update_npc_stats(npc, config)
            
            # 5. 确保位置正确
            if npc.location != location:
                npc.move_to(location, quiet=True)

        self.caller.msg(f"|g处理完成! 新建: {cnt_create}, 更新: {cnt_update}|n")

    def _update_npc_stats(self, npc, config):
        """核心：刷新 NPC 属性"""
        name = config.get('name', npc.key)
        
        # 1. 基础信息
        npc.db.cname = name
        npc.db.color_name = name
        npc.db.desc = config.get('desc', '')
        
        clean_name = strip_ansi(name)
        if clean_name != npc.key:
            npc.aliases.add(clean_name)
            
        # 2. [重要] 初始化 AttrManager 属性 (strength, hp 等)
        AttrManager.init_attributes(npc)
        
        # 3. 应用 stats 配置 (覆盖默认值)
        stats = config.get('stats', {})
        npc.db.stats = stats # 存个备份
        
        for stat_key, val in stats.items():
            # 兼容 yaml 里的 'max_hp' 写法
            if npc.attributes.has(stat_key):
                npc.attributes.add(stat_key, val)
                
                # 如果是 Gauge 类型，同步上限
                # 例如 yaml 写 max_hp: 200 -> db.max_hp = 200 -> db.hp = 200
                if stat_key.startswith('max_'):
                    base_key = stat_key.replace('max_', '') # hp
                    if npc.attributes.has(base_key):
                        npc.attributes.add(base_key, val)
        
        # 4. [新功能] 配置技能
        # yaml 格式: 
        # skills:
        #   - "fireball"
        #   - "heal"
        skills = config.get('skills', [])
        if skills:
            # 转换成字典格式 {'fireball': 1}
            skill_dict = {}
            for s in skills:
                if isinstance(s, str):
                    skill_dict[s] = 1 # 默认 1 级
                elif isinstance(s, dict):
                    # 支持 {"fireball": 5} 写法
                    skill_dict.update(s)
            
            npc.db.learned_skills = skill_dict
            # 自动装备第一个技能到 attack1 槽位 (简单的 AI)
            if skill_dict and not npc.db.skill_slots['attack1']:
                first_skill = list(skill_dict.keys())[0]
                npc.db.skill_slots['attack1'] = first_skill

        # 5. 掉落表
        if 'drops' in config:
            npc.db.drops = config['drops']

        # 6. 最后同步到内存 (让全内存战斗生效)
        if hasattr(npc, 'sync_stats_to_ndb'):
            npc.sync_stats_to_ndb()

    def _parse_yaml_data(self, data):
        """解析各种奇葩 YAML 格式为统一列表"""
        results = []
        raw_items = []
        
        if isinstance(data, dict):
            if 'npcs' in data: # 标准格式
                sub = data['npcs']
                if isinstance(sub, dict): raw_items = sub.items()
                elif isinstance(sub, list): 
                    for i in sub: raw_items.append((None, i))
            else: # 纯字典格式
                raw_items = data.items()
        elif isinstance(data, list): # 纯列表格式
            for i in data: raw_items.append((None, i))
            
        for key, item in raw_items:
            # 尝试提取 key
            final_key = item.get('key') or item.get('prototype_key') or key
            if final_key:
                item['key'] = final_key
                results.append(item)
                
        return results

    def _find_room_unified(self, key):
        if not key or key == 'None': return None
        # 先找 Tag
        found = search_tag(key, category=BATCH_TAG_CATEGORY)
        if found and found[0].is_typeclass("typeclasses.rooms.Room"):
            return found[0]
        # 再找别名
        found = self.caller.search(key, global_search=True, quiet=True)
        if found:
            if isinstance(found, list): found = found[0]
            if found.is_typeclass("typeclasses.rooms.Room"): return found
        return None

    def _list_files(self):
        try:
            path = os.path.join("data", "npcs")
            if not os.path.exists(path): os.makedirs(path)
            files = [f for f in os.listdir(path) if f.endswith('.yaml')]
            self.caller.msg("可用文件: " + ", ".join(files))
        except: pass

# ----------------------------------------------------
# 辅助命令：一键升级全服 NPC (清洗老旧数据)
# ----------------------------------------------------
class CmdNPCUpgradeAll(Command):
    """
    强制升级所有 NPC 到新属性系统
    """
    key = "xx upgrade npcs"
    locks = "cmd:perm(Builder)"
    help_category = "开发"
    
    def func(self):
        from typeclasses.npcs import NPC
        all_npcs = NPC.objects.all()
        count = 0
        self.caller.msg("开始升级全服 NPC ...")
        
        for npc in all_npcs:
            try:
                # 1. 补全属性
                AttrManager.init_attributes(npc)
                
                # 2. 如果有 stats 备份，重新应用
                if npc.db.stats:
                    for k, v in npc.db.stats.items():
                        if npc.attributes.has(k):
                            npc.attributes.add(k, v)
                            # 同步 max_hp -> hp
                            if k == 'max_hp':
                                npc.db.hp = v
                            if k == 'max_qi':
                                npc.db.qi = v
                
                # 3. 同步内存
                if hasattr(npc, 'sync_stats_to_ndb'):
                    npc.sync_stats_to_ndb()
                
                count += 1
            except Exception as e:
                self.caller.msg(f"|r升级 {npc.key} 失败: {e}|n")
                
        self.caller.msg(f"|g升级完成！共处理 {count} 个 NPC。|n")