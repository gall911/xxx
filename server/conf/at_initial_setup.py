"""
At_initial_setup module template

Custom at_initial_setup method. This allows you to hook special
modifications to the initial server startup process. Note that this
will only be run once - when the server starts up for the very first
time! It is called last in the startup process and can thus be used to
overload things that happened before it.

The module must contain a global function at_initial_setup().  This
will be called without arguments. Note that tracebacks in this module
will be QUIETLY ignored, so make sure to check it well to make sure it
does what you expect it to.

"""

# server/conf/at_initial_setup.py
"""
服务器初始化配置
在服务器首次启动时执行一次
"""

def at_initial_setup():
    """
    服务器首次启动时调用
    
    加载所有游戏数据和配置
    """
    from evennia.utils import logger
    
    logger.log_info("=" * 70)
    logger.log_info("修仙MUD服务器 - 初始化开始")
    logger.log_info("=" * 70)
    
    # 1. 加载配置文件
    logger.log_info("\n[步骤1] 加载游戏配置...")
    from world.loaders.config_loader import load_all_configs
    load_all_configs()
    
    # 2. 加载游戏数据
    logger.log_info("\n[步骤2] 加载游戏数据...")
    from world.loaders.data_loader import load_all_data
    load_all_data()
    
    # 3. 验证数据完整性
    logger.log_info("\n[步骤3] 验证数据...")
    from world.loaders.validator import validate_all_data
    from world.loaders.game_data import GAME_DATA
    
    is_valid, errors = validate_all_data(GAME_DATA)
    if not is_valid:
        logger.log_warn(f"数据验证发现 {len(errors)} 个问题")
    
    # 4. 注册技能效果插件
    logger.log_info("\n[步骤4] 注册技能效果插件...")
    from world.systems import skill_effects
    registered = len(skill_effects.EFFECT_REGISTRY)
    logger.log_info(f"已注册 {registered} 个技能效果: {', '.join(skill_effects.get_registered_effects())}")
    
    # 5. 初始化战斗管理器
    logger.log_info("\n[步骤5] 初始化战斗管理器...")
    from world.managers.combat_manager import COMBAT_MANAGER
    logger.log_info("战斗管理器已就绪")
    
    # 6. 创建示例房间（如果需要）
    logger.log_info("\n[步骤6] 检查世界地图...")
    create_initial_rooms()
    
    logger.log_info("\n" + "=" * 70)
    logger.log_info("初始化完成！服务器已准备就绪")
    logger.log_info("=" * 70)


def create_initial_rooms():
    """创建初始房间（新手村等）"""
    from evennia import create_object
    from typeclasses.rooms import Room
    from evennia import search_object
    
    # 检查是否已存在新手村
    existing = search_object("新手村", typeclass=Room)
    if existing:
        from evennia.utils import logger
        logger.log_info("初始房间已存在，跳过创建")
        return
    
    # 创建新手村
    newbie_village = create_object(
        Room,
        key="新手村",
        attributes=[
            ("desc", "这里是所有修仙者开始旅程的地方。\n村子里有几座简陋的茅屋，远处可以看到连绵的山脉。"),
            ("safe_zone", True)
        ]
    )
    
    # 创建修炼场
    training_ground = create_object(
        Room,
        key="修炼场",
        attributes=[
            ("desc", "一片空旷的场地，适合打坐修炼。\n地面上刻着简单的法阵。"),
            ("safe_zone", True)
        ]
    )
    
    # 创建野外
    wilderness = create_object(
        Room,
        key="村外荒野",
        attributes=[
            ("desc", "村子外的荒野，草木茂盛。\n远处传来野兽的吼叫声。"),
            ("safe_zone", False)
        ]
    )
    
    # 连接房间
    from evennia import create_script
    newbie_village.db.exits = {
        "north": training_ground,
        "east": wilderness
    }
    
    training_ground.db.exits = {
        "south": newbie_village
    }
    
    wilderness.db.exits = {
        "west": newbie_village
    }
    
    from evennia.utils import logger
    logger.log_info("已创建初始房间: 新手村, 修炼场, 村外荒野")