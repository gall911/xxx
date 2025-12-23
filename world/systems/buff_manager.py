"""
world/systems/buff_manager.py
回合制Buff管理系统 - 修仙MUD专用
"""
import uuid
from evennia.utils import logger
from world.loaders.game_data import get_config

class BuffManager:
    """
    回合制Buff管理器
    
    核心功能：
    1. 添加/移除Buff
    2. 回合触发（turn_start/turn_end）
    3. 层数管理（叠加/刷新）
    4. 效果执行
    """
    
    @staticmethod
    def add_buff(character, buff_config, source=None, duration=None):
        """
        添加Buff到角色
        
        Args:
            character: 目标角色
            buff_config (dict): Buff配置
                {
                    'type': 'dot/buff/debuff/control',
                    'name': '中毒',
                    'duration': 3,  # 回合数
                    'stacks': 1,    # 当前层数
                    'max_stacks': 5,
                    'stack_mode': 'add/refresh/replace',  # 叠加模式
                    'effects': [
                        {'type': 'damage', 'value': 10, 'element': 'poison'},
                        {'type': 'stat_mod', 'stat': 'defense', 'value': -5}
                    ],
                    'trigger_on': 'turn_start/turn_end',
                    'tick_interval': 1,  # 每N回合触发一次
                }
            source: 施加者（可选）
            duration: 持续回合数（覆盖配置）
        
        Returns:
            str: Buff ID（用于追踪和移除）
        """
        # 初始化buffs列表
        if not hasattr(character.ndb, 'buffs'):
            character.ndb.buffs = []
        
        buff_type = buff_config.get('type', 'buff')
        buff_name = buff_config.get('name', '未命名效果')
        max_stacks = buff_config.get('max_stacks', 1)
        stack_mode = buff_config.get('stack_mode', 'refresh')  # add/refresh/replace
        
        # 检查是否已存在同名Buff
        existing = BuffManager._find_buff_by_name(character, buff_name)
        
        if existing:
            # 处理叠加逻辑
            if stack_mode == 'refresh':
                # 刷新时长
                existing['duration'] = duration or buff_config.get('duration', 3)
                existing['last_tick'] = 0
                character.msg(f"|y{buff_name} 效果刷新！|n")
                return existing['id']
            
            elif stack_mode == 'add':
                # 增加层数
                if existing['stacks'] < max_stacks:
                    existing['stacks'] += 1
                    existing['duration'] = duration or buff_config.get('duration', 3)
                    character.msg(f"|y{buff_name} 叠加到 {existing['stacks']} 层！|n")
                else:
                    existing['duration'] = duration or buff_config.get('duration', 3)
                    character.msg(f"|y{buff_name} 已达最大层数！|n")
                return existing['id']
            
            elif stack_mode == 'replace':
                # 替换旧的
                BuffManager.remove_buff(character, existing['id'])
        
        # 创建新Buff
        buff_id = str(uuid.uuid4())[:8]
        
        new_buff = {
            'id': buff_id,
            'type': buff_type,
            'name': buff_name,
            'source': source,
            'duration': duration or buff_config.get('duration', 3),
            'stacks': buff_config.get('stacks', 1),
            'max_stacks': max_stacks,
            'stack_mode': stack_mode,
            'effects': buff_config.get('effects', []),
            'trigger_on': buff_config.get('trigger_on', 'turn_start'),
            'tick_interval': buff_config.get('tick_interval', 1),
            'last_tick': 0,  # 上次触发的回合
            
            # 可选：图标/描述
            'icon': buff_config.get('icon', ''),
            'desc': buff_config.get('desc', ''),
            
            # 额外数据（用于特殊效果）
            'extra': buff_config.get('extra', {}),
        }
        
        character.ndb.buffs.append(new_buff)
        
        # 显示消息
        BuffManager._show_buff_message(character, new_buff, 'add')
        
        # 如果是属性修改型Buff，立即应用
        BuffManager._apply_stat_modifiers(character, new_buff, apply=True)
        
        logger.log_info(f"[Buff] {character.key} 获得 {buff_name} ({buff_id})")
        
        return buff_id
    
    @staticmethod
    def remove_buff(character, buff_id):
        """
        移除指定Buff
        
        Args:
            character: 目标角色
            buff_id (str): Buff ID
        
        Returns:
            bool: 是否移除成功
        """
        if not hasattr(character.ndb, 'buffs'):
            return False
        
        for i, buff in enumerate(character.ndb.buffs):
            if buff['id'] == buff_id:
                # 移除属性修改
                BuffManager._apply_stat_modifiers(character, buff, apply=False)
                
                # 显示消息
                BuffManager._show_buff_message(character, buff, 'remove')
                
                # 删除
                character.ndb.buffs.pop(i)
                
                logger.log_info(f"[Buff] {character.key} 失去 {buff['name']} ({buff_id})")
                return True
        
        return False
    
    @staticmethod
    def tick_buffs(character, trigger_moment, combat_context=None):
        """
        触发Buff效果（在战斗回合中调用）
        
        Args:
            character: 角色
            trigger_moment (str): 'turn_start' / 'turn_end' / 'on_hit' / 'on_damaged'
            combat_context (dict): 战斗上下文（可选）
        """
        if not hasattr(character.ndb, 'buffs'):
            return
        
        for buff in list(character.ndb.buffs):  # 复制列表，避免迭代时修改
            # 检查触发时机
            if buff['trigger_on'] != trigger_moment:
                continue
            
            # 检查触发间隔
            tick_interval = buff.get('tick_interval', 1)
            if buff['last_tick'] + tick_interval > 0:
                buff['last_tick'] -= 1
                continue
            
            # 重置tick计数
            buff['last_tick'] = tick_interval - 1
            
            # 执行效果
            BuffManager._execute_buff_effects(character, buff, combat_context)
    
    @staticmethod
    def reduce_duration(character):
        """
        减少所有Buff的持续时间（每回合结束调用一次）
        
        Args:
            character: 角色
        """
        if not hasattr(character.ndb, 'buffs'):
            return
        
        expired = []
        
        for buff in character.ndb.buffs:
            buff['duration'] -= 1
            
            if buff['duration'] <= 0:
                expired.append(buff['id'])
        
        # 移除过期的Buff
        for buff_id in expired:
            BuffManager.remove_buff(character, buff_id)
    
    @staticmethod
    def clear_all_buffs(character, buff_type=None):
        """
        清除所有Buff
        
        Args:
            character: 角色
            buff_type (str): 只清除特定类型（可选）'buff'/'debuff'/'dot'
        """
        if not hasattr(character.ndb, 'buffs'):
            return
        
        to_remove = []
        
        for buff in character.ndb.buffs:
            if buff_type is None or buff['type'] == buff_type:
                to_remove.append(buff['id'])
        
        for buff_id in to_remove:
            BuffManager.remove_buff(character, buff_id)
    
    @staticmethod
    def has_buff(character, buff_name):
        """
        检查是否有指定名称的Buff
        
        Args:
            character: 角色
            buff_name (str): Buff名称
        
        Returns:
            bool
        """
        return BuffManager._find_buff_by_name(character, buff_name) is not None
    
    @staticmethod
    def get_buff_stacks(character, buff_name):
        """
        获取Buff的层数
        
        Args:
            character: 角色
            buff_name (str): Buff名称
        
        Returns:
            int: 层数（没有则返回0）
        """
        buff = BuffManager._find_buff_by_name(character, buff_name)
        return buff['stacks'] if buff else 0
    
    # ========================================
    # 内部辅助方法
    # ========================================
    
    @staticmethod
    def _find_buff_by_name(character, buff_name):
        """查找指定名称的Buff"""
        if not hasattr(character.ndb, 'buffs'):
            return None
        
        for buff in character.ndb.buffs:
            if buff['name'] == buff_name:
                return buff
        return None
    
    @staticmethod
    def _execute_buff_effects(character, buff, combat_context):
        """
        执行Buff的效果
        
        Args:
            character: 角色
            buff (dict): Buff数据
            combat_context (dict): 战斗上下文（可选）
        """
        from world.systems.skill_effects import apply_effect
        
        # 创建伪目标（对于DoT等自我伤害效果）
        target = character
        attacker = buff.get('source') or character
        
        context = combat_context or {
            'attacker': attacker,
            'target': target,
            'is_buff_tick': True,
        }
        
        # 应用层数倍率
        stacks = buff.get('stacks', 1)
        
        for effect_config in buff['effects']:
            # 复制效果配置（避免修改原始数据）
            effect = dict(effect_config)
            
            # DoT伤害按层数叠加
            if effect['type'] in ['damage', 'heal', 'restore_qi']:
                if 'value' in effect:
                    effect['value'] = effect['value'] * stacks
            
            # 执行效果
            result = apply_effect(effect, attacker, target, context)
        
        # 显示效果消息（可选）
        if buff.get('show_tick_message', False):
            character.msg(f"|y{buff['name']} 效果触发！|n")
    
    @staticmethod
    def _apply_stat_modifiers(character, buff, apply=True):
        """
        应用/移除属性修改型Buff
        
        Args:
            character: 角色
            buff (dict): Buff数据
            apply (bool): True=应用, False=移除
        """
        multiplier = 1 if apply else -1
        stacks = buff.get('stacks', 1)
        
        for effect in buff['effects']:
            if effect['type'] == 'stat_mod':
                stat_name = effect['stat']
                value = effect['value'] * stacks * multiplier
                
                current = getattr(character.ndb, stat_name, 0) or 0
                setattr(character.ndb, stat_name, current + value)
    
    @staticmethod
    def _show_buff_message(character, buff, action):
        """
        显示Buff消息
        
        Args:
            character: 角色
            buff (dict): Buff数据
            action (str): 'add' / 'remove'
        """
        buff_type = buff['type']
        buff_name = buff['name']
        
        # 根据类型选择颜色
        if buff_type in ['buff', 'hot']:
            color = '|g'
        elif buff_type in ['debuff', 'dot']:
            color = '|r'
        elif buff_type == 'control':
            color = '|m'
        else:
            color = '|y'
        
        if action == 'add':
            duration = buff['duration']
            msg = f"{color}【{buff_name}】效果生效！持续 {duration} 回合|n"
        else:
            msg = f"{color}【{buff_name}】效果消失|n"
        
        character.msg(msg)