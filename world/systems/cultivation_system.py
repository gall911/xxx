# world/systems/cultivation_system.py
"""
修炼系统 - 统一管理升级与突破
包含: 经验系统、等级系统、境界突破
"""

from world.loaders.game_data import get_data, get_config
from world.systems.attr_manager import AttrManager
from world.const import At


class ProgressionManager:
    """升级经验管理器"""
    
    @staticmethod
    def add_exp(character, amount):
        """
        增加经验值
        
        Args:
            character: 角色对象
            amount: 经验值数量
        
        Returns:
            tuple: (是否升级, 升级次数)
        """
        if amount <= 0:
            return False, 0
        
        old_exp = character.db.exp or 0
        character.db.exp = old_exp + amount
        
        # 格式化经验显示
        exp_display = ProgressionManager._format_exp(amount)
        character.msg(f"|g+{exp_display} 经验|n")
        
        # 检查是否升级
        level_up_count = 0
        while ProgressionManager.can_level_up(character):
            if ProgressionManager.do_level_up(character):
                level_up_count += 1
            else:
                break
        
        return level_up_count > 0, level_up_count
    
    @staticmethod
    def can_level_up(character):
        """
        检查是否可以升级
        
        Returns:
            bool: 是否可以升级
        """
        realm_name = character.db.realm
        realm_data = get_data('realms', realm_name)
        
        if not realm_data:
            return False
        
        current_level = character.db.level or 1
        max_level = realm_data.get('max_level', 10)
        
        # 已达该境界最高等级
        if current_level >= max_level:
            return False
        
        # 检查经验是否足够
        current_exp = character.db.exp or 0
        required_exp = ProgressionManager.get_exp_for_next_level(character)
        
        return current_exp >= required_exp
    
    @staticmethod
    def get_exp_for_next_level(character):
        """
        计算升到下一级所需经验
        
        Returns:
            int: 所需经验值
        """
        realm_name = character.db.realm
        realm_data = get_data('realms', realm_name)
        
        if not realm_data:
            return 999999999
        
        current_level = character.db.level or 1
        exp_curve = realm_data.get('exp_curve', {})
        
        base_exp = exp_curve.get('base', 100)
        multiplier = exp_curve.get('multiplier', 1.5)
        
        # 计算公式: base * (multiplier ^ (level - 1))
        required_exp = int(base_exp * (multiplier ** (current_level - 1)))
        
        return required_exp
    
    @staticmethod
    def do_level_up(character):
        """
        执行升级
        
        Returns:
            bool: 是否升级成功
        """
        realm_name = character.db.realm
        realm_data = get_data('realms', realm_name)
        
        if not realm_data:
            return False
        
        # 扣除经验
        required_exp = ProgressionManager.get_exp_for_next_level(character)
        character.db.exp -= required_exp
        
        # 升级
        old_level = character.db.level or 1
        character.db.level = old_level + 1
        
        # 应用等级成长
        level_growth = realm_data.get('level_growth', {})
        for attr, growth_value in level_growth.items():
            AttrManager.modify_attr(character, attr, growth_value)
        
        # 升级消息
        level_up_msg = get_config('progression.level_up_message', '|y✨ 恭喜升级！|n')
        character.msg("|y" + "=" * 50)
        character.msg(level_up_msg)
        character.msg(f"|c等级: {old_level} → {character.db.level}|n")
        
        # 显示属性成长
        if level_growth:
            character.msg("\n|g属性提升:|n")
            for attr, value in level_growth.items():
                attr_name = AttrManager.get_name(attr)
                character.msg(f"  {attr_name}: +{value}")
        
        character.msg("|y" + "=" * 50)
        
        # 是否回满血蓝
        if get_config('progression.level_up_restore_hp', True):
            max_hp = AttrManager.get_attr(character, At.MAX_HP)
            AttrManager.set_attr(character, At.HP, max_hp)
        
        if get_config('progression.level_up_restore_qi', True):
            max_qi = AttrManager.get_attr(character, At.MAX_QI)
            AttrManager.set_attr(character, At.QI, max_qi)
        
        # 检查是否满级 (提示可突破)
        max_level = realm_data.get('max_level', 10)
        if character.db.level >= max_level:
            if get_config('breakthrough.auto_prompt_when_max_level', True):
                character.msg("\n|y💫 你已达到该境界的巅峰！|n")
                character.msg("|c可以尝试突破到下一境界。输入 '突破' 查看要求。|n")
        
        return True
    
    @staticmethod
    def _format_exp(exp):
        """
        格式化经验显示
        例: 1500000 → 1.5M
        """
        threshold = get_config('progression.exp_display_threshold', 1000000)
        
        if exp >= threshold:
            return f"{exp / 1000000:.1f}M"
        elif exp >= 1000:
            return f"{exp / 1000:.1f}K"
        else:
            return str(exp)


class BreakthroughManager:
    """境界突破管理器"""
    
    @staticmethod
    def can_breakthrough(character):
        """
        检查是否可以突破
        
        Returns:
            tuple: (是否可以, 失败原因列表)
        """
        realm_name = character.db.realm
        realm_data = get_data('realms', realm_name)
        
        if not realm_data:
            return False, ["境界数据错误"]
        
        # 检查是否已是最高境界
        next_realm = realm_data.get('next_realm')
        if not next_realm:
            return False, ["你已达到最高境界"]
        
        reqs = realm_data.get('breakthrough_requirements', {})
        if not reqs:
            return False, ["该境界无法突破"]
        
        failures = []
        
        # 1. 检查等级
        required_level = reqs.get('level', 0)
        current_level = character.db.level or 1
        if current_level < required_level:
            failures.append(f"等级不足 (需要 {required_level}级，当前 {current_level}级)")
        
        # 2. 检查门派贡献
        required_contribution = reqs.get('sect_contribution', 0)
        if required_contribution > 0:
            current_contribution = character.attributes.get(At.SECT_CONTRIBUTION) or 0
            if current_contribution < required_contribution:
                failures.append(
                    f"门派贡献不足 (需要 {required_contribution}，当前 {current_contribution})"
                )
        
        # 3. 检查物品
        required_items = reqs.get('items', {})
        for item_key, amount in required_items.items():
            if hasattr(character, 'has_item'):
                if not character.has_item(item_key, amount):
                    failures.append(f"缺少物品: {item_key} ×{amount}")
        
        # 4. 检查任务
        required_tasks = reqs.get('tasks', [])
        for task_name in required_tasks:
            # TODO: 接入任务系统
            # if not character.has_completed_quest(task_name):
            #     failures.append(f"未完成任务: {task_name}")
            pass
        
        return len(failures) == 0, failures
    
    @staticmethod
    def do_breakthrough(character):
        """
        执行突破
        
        Returns:
            tuple: (是否成功, 消息)
        """
        # 检查条件
        can_break, failures = BreakthroughManager.can_breakthrough(character)
        
        # 测试模式可跳过检查
        if not can_break and not get_config('breakthrough.allow_skip_requirements', False):
            msg = "|r无法突破:|n\n"
            for fail in failures:
                msg += f"  • {fail}\n"
            return False, msg
        
        realm_name = character.db.realm
        realm_data = get_data('realms', realm_name)
        next_realm = realm_data.get('next_realm')
        
        # 消耗物品
        reqs = realm_data.get('breakthrough_requirements', {})
        required_items = reqs.get('items', {})
        
        for item_key, amount in required_items.items():
            if hasattr(character, 'take_item'):
                character.take_item(item_key, amount)
        
        # 突破成功率判定
        success_rate = get_config('breakthrough.breakthrough_success_rate', 1.0)
        import random
        success = random.random() < success_rate
        
        if not success:
            return False, "|r突破失败！需要继续修炼...|n"
        
        # 突破成功
        old_realm = character.db.realm
        character.db.realm = next_realm
        character.db.level = 1  # 重置等级
        character.db.exp = 0    # 重置经验
        
        # 应用新境界属性
        AttrManager.apply_realm_stats(character)
        
        # 是否满血满蓝
        if get_config('breakthrough.breakthrough_restore_full', True):
            max_hp = AttrManager.get_attr(character, At.MAX_HP)
            max_qi = AttrManager.get_attr(character, At.MAX_QI)
            AttrManager.set_attr(character, At.HP, max_hp)
            AttrManager.set_attr(character, At.QI, max_qi)
        
        # 生成突破消息
        next_realm_data = get_data('realms', next_realm)
        
        msg = "|y" + "=" * 60 + "\n"
        msg += "|g✨【突破成功】✨|n\n"
        msg += "|y" + "=" * 60 + "\n\n"
        msg += f"|c{old_realm} → {next_realm}|n\n\n"
        
        if next_realm_data:
            desc = next_realm_data.get('desc', '')
            msg += f"{desc}\n\n"
            
            # 显示属性变化
            base_stats = next_realm_data.get('base_stats', {})
            if base_stats:
                msg += "|g属性飙升:|n\n"
                for attr, value in base_stats.items():
                    attr_name = AttrManager.get_name(attr)
                    msg += f"  {attr_name}: {value}\n"
        
        msg += "\n|y" + "=" * 60
        
        return True, msg
    
    @staticmethod
    def get_breakthrough_info(character):
        """
        获取突破信息
        
        Returns:
            str: 突破信息文本
        """
        realm_name = character.db.realm
        realm_data = get_data('realms', realm_name)
        
        if not realm_data:
            return "|r境界数据错误|n"
        
        next_realm = realm_data.get('next_realm')
        if not next_realm:
            return "|y你已达到最高境界！|n"
        
        reqs = realm_data.get('breakthrough_requirements', {})
        if not reqs:
            return "|r该境界无突破配置|n"
        
        msg = "|c" + "=" * 50 + "\n"
        msg += f"突破到 |y{next_realm}|c 的条件:\n"
        msg += "=" * 50 + "\n\n"
        
        # 等级要求
        required_level = reqs.get('level', 0)
        current_level = character.db.level or 1
        status = "|g✓|n" if current_level >= required_level else "|r✗|n"
        msg += f"{status} 等级: {current_level}/{required_level}\n"
        
        # 门派贡献
        required_contribution = reqs.get('sect_contribution', 0)
        if required_contribution > 0:
            current_contribution = character.attributes.get(At.SECT_CONTRIBUTION) or 0
            status = "|g✓|n" if current_contribution >= required_contribution else "|r✗|n"
            msg += f"{status} 门派贡献: {current_contribution}/{required_contribution}\n"
        
        # 物品要求
        required_items = reqs.get('items', {})
        if required_items:
            msg += "\n|y需要物品:|n\n"
            for item_key, amount in required_items.items():
                has_count = 0
                if hasattr(character, 'has_item'):
                    # 获取实际拥有数量 (需要改造 has_item 支持返回数量)
                    has_count = amount if character.has_item(item_key, amount) else 0
                
                status = "|g✓|n" if has_count >= amount else "|r✗|n"
                msg += f"  {status} {item_key}: {has_count}/{amount}\n"
        
        # 任务要求
        required_tasks = reqs.get('tasks', [])
        if required_tasks:
            msg += "\n|y需要完成任务:|n\n"
            for task_name in required_tasks:
                # TODO: 接入任务系统
                status = "|g✓|n"  # 暂时默认完成
                msg += f"  {status} {task_name}\n"
        
        msg += "\n|c" + "=" * 50
        
        return msg