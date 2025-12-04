"""
任务目标处理器 - 插件式注册系统
所有目标类型通过注册器添加,不修改核心代码
"""

# 目标处理器注册表
_OBJECTIVE_HANDLERS = {}

def register_objective_handler(obj_type, handler):
    """
    注册目标处理器
    
    Args:
        obj_type: 目标类型 ('kill', 'collect', 'talk', 等)
        handler: 处理器类实例
    """
    _OBJECTIVE_HANDLERS[obj_type] = handler

def get_objective_handler(obj_type):
    """获取目标处理器"""
    return _OBJECTIVE_HANDLERS.get(obj_type)

# ============================================
# 基础目标处理器接口
# ============================================

class BaseObjectiveHandler:
    """目标处理器基类"""
    
    def check_progress(self, character, objective, event_data):
        """
        检查并更新进度
        
        Args:
            character: 角色对象
            objective: 目标配置 (dict)
            event_data: 事件数据 (dict)
        
        Returns:
            bool: 是否有进度更新
        """
        raise NotImplementedError
    
    def is_completed(self, objective):
        """检查目标是否完成"""
        raise NotImplementedError
    
    def get_progress_text(self, objective):
        """获取进度文本"""
        raise NotImplementedError

# ============================================
# 具体目标处理器实现
# ============================================

class KillObjectiveHandler(BaseObjectiveHandler):
    """击杀目标"""
    
    def check_progress(self, character, objective, event_data):
        target = objective.get('target')
        required = objective.get('count', 1)
        
        # 检查目标是否匹配
        if event_data.get('target') != target:
            return False
        
        # 更新进度
        objective['current'] = objective.get('current', 0) + 1
        
        return True
    
    def is_completed(self, objective):
        current = objective.get('current', 0)
        required = objective.get('count', 1)
        return current >= required
    
    def get_progress_text(self, objective):
        target = objective.get('target', '目标')
        current = objective.get('current', 0)
        required = objective.get('count', 1)
        return f"击杀 {target} ({current}/{required})"

class CollectObjectiveHandler(BaseObjectiveHandler):
    """收集目标"""
    
    def check_progress(self, character, objective, event_data):
        target_item = objective.get('target')
        required = objective.get('count', 1)
        
        # 检查物品是否匹配
        if event_data.get('item') != target_item:
            return False
        
        # 更新进度
        collect_count = event_data.get('count', 1)
        objective['current'] = objective.get('current', 0) + collect_count
        
        return True
    
    def is_completed(self, objective):
        current = objective.get('current', 0)
        required = objective.get('count', 1)
        return current >= required
    
    def get_progress_text(self, objective):
        target = objective.get('target', '物品')
        current = objective.get('current', 0)
        required = objective.get('count', 1)
        return f"收集 {target} ({current}/{required})"

class TalkObjectiveHandler(BaseObjectiveHandler):
    """对话目标"""
    
    def check_progress(self, character, objective, event_data):
        target_npc = objective.get('target')
        
        # 检查NPC是否匹配
        if event_data.get('npc') != target_npc:
            return False
        
        # 标记为已对话
        objective['talked'] = True
        
        return True
    
    def is_completed(self, objective):
        return objective.get('talked', False)
    
    def get_progress_text(self, objective):
        target = objective.get('target', 'NPC')
        talked = objective.get('talked', False)
        return f"与 {target} 对话 ({'已完成' if talked else '未完成'})"

class ExploreObjectiveHandler(BaseObjectiveHandler):
    """探索目标"""
    
    def check_progress(self, character, objective, event_data):
        target_location = objective.get('target')
        
        # 检查地点是否匹配
        if event_data.get('location') != target_location:
            return False
        
        # 标记为已探索
        objective['visited'] = True
        
        return True
    
    def is_completed(self, objective):
        return objective.get('visited', False)
    
    def get_progress_text(self, objective):
        target = objective.get('target', '地点')
        visited = objective.get('visited', False)
        return f"探索 {target} ({'已完成' if visited else '未完成'})"

class CultivateObjectiveHandler(BaseObjectiveHandler):
    """修炼目标"""
    
    def check_progress(self, character, objective, event_data):
        duration = event_data.get('duration', 0)
        
        # 累加修炼时长
        objective['current'] = objective.get('current', 0) + duration
        
        return True
    
    def is_completed(self, objective):
        current = objective.get('current', 0)
        required = objective.get('duration', 0)
        return current >= required
    
    def get_progress_text(self, objective):
        current = objective.get('current', 0)
        required = objective.get('duration', 0)
        
        # 转换为分钟显示
        current_min = current // 60
        required_min = required // 60
        
        return f"修炼时长 ({current_min}/{required_min}分钟)"

class UseSkillObjectiveHandler(BaseObjectiveHandler):
    """使用技能目标 - 扩展示例"""
    
    def check_progress(self, character, objective, event_data):
        target_skill = objective.get('target')
        required = objective.get('count', 1)
        
        # 检查技能是否匹配
        if event_data.get('skill') != target_skill:
            return False
        
        # 更新使用次数
        objective['current'] = objective.get('current', 0) + 1
        
        return True
    
    def is_completed(self, objective):
        current = objective.get('current', 0)
        required = objective.get('count', 1)
        return current >= required
    
    def get_progress_text(self, objective):
        skill = objective.get('target', '技能')
        current = objective.get('current', 0)
        required = objective.get('count', 1)
        return f"使用 {skill} ({current}/{required}次)"

class CraftObjectiveHandler(BaseObjectiveHandler):
    """制作物品目标 - 扩展示例"""
    
    def check_progress(self, character, objective, event_data):
        target_item = objective.get('target')
        required = objective.get('count', 1)
        
        # 检查制作物品
        if event_data.get('item') != target_item:
            return False
        
        # 更新制作数量
        craft_count = event_data.get('count', 1)
        objective['current'] = objective.get('current', 0) + craft_count
        
        return True
    
    def is_completed(self, objective):
        current = objective.get('current', 0)
        required = objective.get('count', 1)
        return current >= required
    
    def get_progress_text(self, objective):
        item = objective.get('target', '物品')
        current = objective.get('current', 0)
        required = objective.get('count', 1)
        return f"制作 {item} ({current}/{required})"

# ============================================
# 自动注册所有处理器
# ============================================

def init_objective_handlers():
    """初始化所有目标处理器"""
    register_objective_handler('kill', KillObjectiveHandler())
    register_objective_handler('collect', CollectObjectiveHandler())
    register_objective_handler('talk', TalkObjectiveHandler())
    register_objective_handler('explore', ExploreObjectiveHandler())
    register_objective_handler('cultivate', CultivateObjectiveHandler())
    register_objective_handler('use_skill', UseSkillObjectiveHandler())
    register_objective_handler('craft', CraftObjectiveHandler())

# 模块导入时自动初始化
init_objective_handlers()
class YourNewObjectiveHandler(BaseObjectiveHandler):
    """你的新目标类型"""
    
    def check_progress(self, character, objective, event_data):
        # 实现进度检查逻辑
        pass
    
    def is_completed(self, objective):
        # 实现完成判断
        pass
    
    def get_progress_text(self, objective):
        # 实现进度文本
        pass

# 注册
register_objective_handler('your_type', YourNewObjectiveHandler())