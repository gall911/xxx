# commands/dev/zone_commands.py
"""区域管理命令 - 智能同步版"""

from evennia import Command


class CmdSyncZone(Command):
    """
    🔥 智能同步区域 (推荐)
    
    用法:
      synczone <区域名>           # 增量更新
      synczone <区域名> force     # 强制更新所有对象
      synczone all                # 同步所有区域
    
    功能:
      - 新增YAML里有但DB里没有的对象
      - 更新YAML里修改过的对象
      - 删除YAML里没有但DB里有的对象
      - 保留玩家运行时数据 (如NPC战斗状态)
    
    例子:
      synczone newbie_village
      # → 房间描述改了会更新
      # → 新增了铁匠会创建
      # → 删除的NPC会移除
      # → 但玩家装饰/GM调整会保留
    """
    key = "synczone"
    locks = "cmd:perm(Builder)"
    help_category = "区域管理"
    
    def func(self):
        from world.systems.zone_manager import ZoneManager
        
        if not self.args:
            self.caller.msg("用法: synczone <区域名> [force]")
            return
        
        args = self.args.split()
        zone_key = args[0]
        force = len(args) > 1 and args[1] == 'force'
        
        if zone_key == 'all':
            # 同步所有区域
            zones = ZoneManager.list_all_zones()
            self.caller.msg(f"|y开始同步所有区域...|n")
            
            for zk in zones.keys():
                self.caller.msg(f"\n|c同步: {zk}|n")
                stats = ZoneManager.sync_zone(zk, force)
                self._show_stats(stats)
            
            self.caller.msg(f"\n|g所有区域同步完成！|n")
        else:
            # 同步单个区域
            self.caller.msg(f"|y开始同步区域: {zone_key}|n")
            
            if force:
                self.caller.msg("|r强制更新模式: 所有对象将被更新|n")
            
            stats = ZoneManager.sync_zone(zone_key, force)
            
            if 'error' in stats:
                self.caller.msg(f"|r错误: {stats['error']}|n")
                return
            
            self._show_stats(stats)
            self.caller.msg(f"\n|g区域同步完成！|n")
    
    def _show_stats(self, stats):
        """显示同步统计"""
        self.caller.msg(f"  创建: |g{stats.get('created', 0)}|n 个对象")
        self.caller.msg(f"  更新: |y{stats.get('updated', 0)}|n 个对象")
        self.caller.msg(f"  删除: |r{stats.get('deleted', 0)}|n 个对象")
        self.caller.msg(f"  未变: |x{stats.get('unchanged', 0)}|n 个对象")


class CmdBuildZone(Command):
    """
    建造区域 (首次创建)
    
    用法:
      buildzone <区域名>
    
    注意:
      如果区域已存在,会跳过。使用 synczone 进行更新。
    """
    key = "buildzone"
    locks = "cmd:perm(Builder)"
    help_category = "区域管理"
    
    def func(self):
        from world.systems.zone_manager import ZoneManager
        
        zone_key = self.args.strip()
        if not zone_key:
            self.caller.msg("用法: buildzone <区域名>")
            return
        
        # 检查是否已建造
        if ZoneManager.is_zone_built(zone_key):
            self.caller.msg(f"|y区域 {zone_key} 已存在。|n")
            self.caller.msg(f"使用 |csynczone {zone_key}|n 进行更新。")
            return
        
        self.caller.msg(f"|y开始建造区域: {zone_key}|n")
        
        success = ZoneManager.build_zone(zone_key)
        
        if success:
            self.caller.msg(f"|g区域建造完成！|n")
        else:
            self.caller.msg(f"|r建造失败，请检查配置文件。|n")


class CmdActivateZone(Command):
    """
    激活区域 (显示给玩家)
    
    用法:
      activatezone <区域名>
    
    效果:
      - 所有NPC回到出生点
      - 所有房间变为可见
      - 玩家可以进入
    """
    key = "activatezone"
    locks = "cmd:perm(Builder)"
    help_category = "区域管理"
    
    def func(self):
        from world.systems.zone_manager import ZoneManager
        
        zone_key = self.args.strip()
        if not zone_key:
            self.caller.msg("用法: activatezone <区域名>")
            return
        
        if not ZoneManager.is_zone_built(zone_key):
            self.caller.msg(f"|r区域 {zone_key} 不存在，请先使用 buildzone 建造。|n")
            return
        
        ZoneManager.activate_zone(zone_key)
        self.caller.msg(f"|g区域 {zone_key} 已激活！|n")


class CmdDeactivateZone(Command):
    """
    休眠区域 (隐藏不删除)
    
    用法:
      deactivatezone <区域名>
    
    效果:
      - 所有NPC移到Limbo (消失)
      - 所有房间隐藏
      - 玩家无法进入
      - 🔥 DB对象保留,可快速重新激活
    """
    key = "deactivatezone"
    locks = "cmd:perm(Builder)"
    help_category = "区域管理"
    
    def func(self):
        from world.systems.zone_manager import ZoneManager
        
        zone_key = self.args.strip()
        if not zone_key:
            self.caller.msg("用法: deactivatezone <区域名>")
            return
        
        ZoneManager.deactivate_zone(zone_key)
        self.caller.msg(f"|y区域 {zone_key} 已休眠。|n")


class CmdDestroyZone(Command):
    """
    彻底删除区域 (危险操作)
    
    用法:
      destroyzone <区域名> confirm
    
    警告:
      - 会删除所有DB对象
      - 玩家装饰/GM调整全部丢失
      - 只在重新开始时使用
    """
    key = "destroyzone"
    locks = "cmd:perm(Admin)"  # 只有Admin可用
    help_category = "区域管理"
    
    def func(self):
        from world.systems.zone_manager import ZoneManager
        
        args = self.args.split()
        if len(args) < 2 or args[1] != 'confirm':
            self.caller.msg("|r危险操作！|n")
            self.caller.msg(f"用法: destroyzone <区域名> confirm")
            self.caller.msg("这会彻底删除区域的所有对象！")
            return
        
        zone_key = args[0]
        
        self.caller.msg(f"|r警告: 即将删除区域 {zone_key} 的所有对象...|n")
        
        ZoneManager.destroy_zone(zone_key)
        
        self.caller.msg(f"|r区域 {zone_key} 已彻底删除。|n")


class CmdListZones(Command):
    """
    列出所有区域
    
    用法:
      zones
      zones <区域名>  # 显示详细信息
    """
    key = "zones"
    locks = "cmd:perm(Builder)"
    help_category = "区域管理"
    
    def func(self):
        from world.systems.zone_manager import ZoneManager
        
        if not self.args:
            # 列出所有区域
            zones = ZoneManager.list_all_zones()
            
            self.caller.msg("|c" + "=" * 70)
            self.caller.msg("区域列表")
            self.caller.msg("=" * 70 + "|n")
            self.caller.msg(f"{'区域名':<25} {'状态':<10} {'对象数':<10} {'已建造':<10}")
            self.caller.msg("|c" + "-" * 70 + "|n")
            
            for zone_key, info in sorted(zones.items()):
                status = "|g激活|n" if info['active'] else "|y休眠|n"
                built = "|g✓|n" if info['built'] else "|r✗|n"
                count = info['object_count']
                
                self.caller.msg(f"{zone_key:<25} {status:<10} {count:<10} {built:<10}")
            
            self.caller.msg("|c" + "=" * 70 + "|n")
            self.caller.msg("\n提示: zones <区域名> 查看详细信息")
        
        else:
            # 显示详细信息
            zone_key = self.args.strip()
            config = ZoneManager.load_zone_config(zone_key)
            
            if not config:
                self.caller.msg(f"|r区域 {zone_key} 不存在。|n")
                return
            
            zone_info = config.get('zone', {}).get('zone', {})
            version_info = config.get('version', {}).get('version', {})
            
            self.caller.msg("|c" + "=" * 50)
            self.caller.msg(f"区域详情: {zone_key}")
            self.caller.msg("=" * 50 + "|n")
            
            self.caller.msg(f"\n名称: {zone_info.get('name', zone_key)}")
            self.caller.msg(f"描述: {zone_info.get('desc', '无')}")
            self.caller.msg(f"入口: {zone_info.get('entry_room', '无')}")
            
            if version_info:
                self.caller.msg(f"\n版本: {version_info.get('current', '未知')}")
                self.caller.msg(f"最后同步: {version_info.get('last_sync', '从未')}")
            
            # 统计
            rooms_count = len(config.get('rooms', {}).get('rooms', {}))
            npcs_count = len(config.get('npcs', {}).get('npcs', {}))
            
            self.caller.msg(f"\n房间数: {rooms_count}")
            self.caller.msg(f"NPC数: {npcs_count}")
            
            self.caller.msg("|c" + "=" * 50 + "|n")