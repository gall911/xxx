# world/loaders/data_loader.py
"""游戏数据加载器 - 加载YAML配置到内存"""
import yaml
from pathlib import Path
from evennia.utils import logger
from .game_data import GAME_DATA
from copy import deepcopy

def load_yaml_files_in_dir(dir_path, data_key=None):
    """
    递归加载目录下所有YAML文件，合并为一个字典
    
    Args:
        dir_path: 目录路径（Path对象或字符串）
        data_key: YAML中的顶层key（如'items', 'rooms'），None则直接合并所有内容
    
    Returns:
        dict: 合并后的数据字典
    """
    result = {}
    dir_path = Path(dir_path)
    
    if not dir_path.exists():
        logger.log_warn(f"数据目录不存在: {dir_path}")
        return result
    
    # 递归查找所有.yaml文件（支持子目录）
    yaml_files = list(dir_path.rglob('*.yaml'))
    
    for yaml_file in yaml_files:
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
                if not data:
                    continue
                
                # 根据data_key提取数据
                if data_key and data_key in data:
                    # 格式1: items: {聚气丹: {...}}
                    to_merge = data[data_key]
                elif data_key:
                    # 格式2: 直接定义，兼容处理
                    to_merge = data
                else:
                    # 无data_key，直接合并
                    to_merge = data
                
                # 检查key冲突
                for key in to_merge:
                    if key in result:
                        logger.log_warn(
                            f"[数据] 发现重复key '{key}' "
                            f"在 {yaml_file.name}，将覆盖旧值"
                        )
                
                result.update(to_merge)
                
        except yaml.YAMLError as e:
            logger.log_err(f"[数据] YAML解析错误 {yaml_file.name}: {e}")
        except Exception as e:
            logger.log_err(f"[数据] 加载失败 {yaml_file.name}: {e}")
    
    return result

def load_single_yaml(file_path):
    """
    加载单个YAML文件
    
    Args:
        file_path: 文件路径
    
    Returns:
        dict: YAML内容
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.log_warn(f"文件不存在: {file_path}")
        return {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        logger.log_err(f"[数据] 加载失败 {file_path.name}: {e}")
        return {}

def load_skills_with_inheritance(base_path='data/skills'):
    """
    加载技能配置，支持继承
    
    Returns:
        dict: {skill_key: skill_config}
    """
    base_path = Path(base_path)
    all_skills = {}
    base_configs = {}
    
    # 1. 先加载所有base配置
    base_dir = base_path / 'base'
    if base_dir.exists():
        for yaml_file in base_dir.rglob('*.yaml'):
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f) or {}
                    base_configs.update(data)
                    logger.log_info(f"[技能] 加载基础配置: {yaml_file.name}")
            except Exception as e:
                logger.log_err(f"[技能] 加载失败 {yaml_file.name}: {e}")
    
    # 2. 加载所有技能配置
    for yaml_file in base_path.rglob('*.yaml'):
        if 'base' in yaml_file.parts:
            continue  # 跳过base目录
        
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
                
                # 兼容旧格式：skills: {...}
                if 'skills' in data:
                    data = data['skills']
                
                for skill_key, skill_config in data.items():
                    # 处理继承
                    if 'inherit' in skill_config:
                        inherit_key = skill_config['inherit']
                        if inherit_key in base_configs:
                            # 深拷贝基础配置
                            final_config = deepcopy(base_configs[inherit_key])
                            # 合并当前配置（覆盖基础配置）
                            _deep_merge(final_config, skill_config)
                            all_skills[skill_key] = final_config
                        else:
                            logger.log_warn(f"[技能] {skill_key} 继承的基础配置 {inherit_key} 不存在")
                            all_skills[skill_key] = skill_config
                    else:
                        all_skills[skill_key] = skill_config
                
                logger.log_info(f"[技能] 加载: {yaml_file.name}")
        except Exception as e:
            logger.log_err(f"[技能] 加载失败 {yaml_file.name}: {e}")
    
    return all_skills

def _deep_merge(base, override):
    """
    深度合并字典
    override 的值会覆盖 base
    """
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _deep_merge(base[key], value)
        else:
            base[key] = value

def load_all_data():
    """
    加载所有游戏数据到 GAME_DATA 全局字典
    启动时调用一次
    """

    logger.log_info("=" * 60)
    logger.log_info("开始加载游戏数据...")
    logger.log_info("=" * 60)
    
    base_path = Path('data')
    
    # 1. 加载境界配置
    realms_data = load_single_yaml(base_path / 'realms.yaml')
    GAME_DATA['realms'] = realms_data.get('realms', realms_data)
    logger.log_info(f"[数据] 境界: {len(GAME_DATA['realms'])} 个")
    
    # 2. 加载物品（递归加载items/base/目录）
    GAME_DATA['items'] = load_yaml_files_in_dir(
        base_path / 'items' / 'base', 
        'items'
    )
    logger.log_info(f"[数据] 物品: {len(GAME_DATA['items'])} 个")
    
    # 3. 加载词条库
    affixes_data = load_single_yaml(base_path / 'items' / 'affixes.yaml')
    GAME_DATA['affixes'] = affixes_data.get('affixes', {})
    logger.log_info(f"[数据] 词条: {len(GAME_DATA['affixes'])} 个")
    
    # 4. 加载合成配方
    recipes_data = load_single_yaml(base_path / 'items' / 'recipes.yaml')
    GAME_DATA['recipes'] = recipes_data.get('recipes', {})
    logger.log_info(f"[数据] 配方: {len(GAME_DATA['recipes'])} 个")
    
    # 5. 加载技能（支持继承）
    GAME_DATA['skills'] = load_skills_with_inheritance(base_path / 'skills')
    logger.log_info(f"[数据] 技能: {len(GAME_DATA['skills'])} 个")
    
    # 6. 加载NPC
    GAME_DATA['npcs'] = load_yaml_files_in_dir(
        base_path / 'npcs', 
        'npcs'
    )
    logger.log_info(f"[数据] NPC: {len(GAME_DATA['npcs'])} 个")
    
    # 7. 加载房间
    GAME_DATA['rooms'] = load_yaml_files_in_dir(
        base_path / 'rooms', 
        'rooms'
    )
    logger.log_info(f"[数据] 房间: {len(GAME_DATA['rooms'])} 个")

    # 8. 加载任务
    GAME_DATA['quests'] = load_yaml_files_in_dir(
        base_path / 'quests',
        'quests'
    )
    logger.log_info(f"[数据] 任务: {len(GAME_DATA['quests'])} 个")
    
    
    logger.log_info("=" * 60)
    logger.log_info("游戏数据加载完成！")
    logger.log_info("=" * 60)