"""
commands/dev/test_commands.py
性能测试套件 - 完整版
"""
import time
import psutil
import os
import sys
import random  # <--- 刚才报错就是缺这个
from evennia import Command, create_object
from evennia.utils import search
from django.conf import settings
from world.const import At

class CmdTestCombatDebug(Command):
    """
    [Debug模式] 交互式战斗测试
    1. 手动驱动战斗逻辑 (模拟 Ticker)
    2. 实时显示进度
    3. 验证内存 HP 变动
    
    Usage:
        test_combat_debug <NPC数量> <持续时间>
    """
    key = "test_combat_debug"
    help_category = "Developers"

    def func(self):
        # 参数解析
        if not self.args or len(self.args.split()) < 2:
            self.msg("|r用法: test_combat_debug <NPC数量> <持续秒数>|n")
            return
        
        try:
            count = int(self.args.split()[0])
            duration = int(self.args.split()[1])
        except ValueError:
            self.msg("|r参数必须是数字。|n")
            return

        if count % 2 != 0: count += 1

        self.msg(f"|g=== ⚔️ 激战测试 (单位: {count}, 时长: {duration}s) ===|n")
        self.msg("|y注意：测试后请运行 clear_mobs 清理现场|n")

        monitor = PerformanceMonitor()
        
        # === 1. 创建 ===
        monitor.start_phase("Creation")
        npcs = []
        for i in range(count):
            # 确保这里的 typeclass 路径是对的，如果报错改成 typeclasses.npcs.NPC
            mob = create_object("typeclasses.npcs.Monster", 
                              key=f"DEBUG_MOB_{i}", 
                              location=self.caller.location)
            mob.db.hp = 100000 
            mob.db.max_hp = 100000
            # 这里的 sync 可能需要根据你的 characters.py 确认方法名
            if hasattr(mob, 'sync_stats_to_ndb'):
                mob.sync_stats_to_ndb()
            else:
                # 兼容防错
                mob.ndb.hp = mob.db.hp
                
            mob.ndb.debug_start_hp = mob.ndb.hp
            npcs.append(mob)
        monitor.end_phase()
        
        # === 2. 战斗循环 (主动驱动) ===
        self.msg(f"|w[战斗开始] 正在模拟 {count//2} 对厮杀...|n")
        monitor.start_phase("Combat")
        
        start_time = time.time()
        next_report = start_time + 1
        
        # 记录总攻击次数
        total_attacks = 0
        
        while time.time() - start_time < duration:
            # --- 模拟 Ticker: 每一轮循环代表一次心跳 ---
            
            # 遍历每一对，互相攻击
            pairs = count // 2
            for i in range(pairs):
                attacker = npcs[i*2]
                target = npcs[i*2 + 1]
                
                # [关键] 模拟内存伤害计算
                dmg1 = random.randint(100, 500)
                if hasattr(target.ndb, 'hp'):
                    target.ndb.hp -= dmg1
                
                dmg2 = random.randint(100, 500)
                if hasattr(attacker.ndb, 'hp'):
                    attacker.ndb.hp -= dmg2
                    
                total_attacks += 2

            # --- 进度条反馈 ---
            now = time.time()
            if now >= next_report:
                elapsed = int(now - start_time)
                progress = int((elapsed / duration) * 20)
                # 防止除零错误
                if duration > 0:
                    bar = "|" + "=" * progress + "-" * (20 - progress) + "|"
                else:
                    bar = "|DONE|"
                
                # 抽查第一个怪的血量给玩家看
                sample_hp = getattr(npcs[0].ndb, 'hp', 'Unknown')
                self.msg(f"{bar} {elapsed}/{duration}s | APS: {total_attacks//(elapsed or 1)} | Mob_0 HP: {sample_hp}")
                next_report = now + 1
            
            # 稍微睡一下防止 CPU 100%
            time.sleep(0.5)

        monitor.end_phase()
        
        # === 3. 待机验证 ===
        self.msg(f"|w[待机] 验证磁盘静默...|n")
        monitor.start_phase("Idle/NoDel")
        time.sleep(2) 
        monitor.end_phase()

        # === 结果验证 ===
        self.msg("\n|y=== 战后清算 ===|n")
        
        # 统计受伤情况
        damaged_mobs = 0
        total_dmg_dealt = 0
        
        for mob in npcs:
            start = getattr(mob.ndb, 'debug_start_hp', 0)
            curr = getattr(mob.ndb, 'hp', 0)
            diff = start - curr
            if diff != 0:
                damaged_mobs += 1
                total_dmg_dealt += diff
        
        self.msg(f"参战单位: {count}")
        self.msg(f"受伤单位: {damaged_mobs} (预期: {count})")
        self.msg(f"总计造成伤害: {total_dmg_dealt}")

        # === 性能报告 ===
        self.msg(monitor.get_report())


class CmdClearDebugMobs(Command):
    """
    清理 debug 产生的垃圾 NPC
    """
    key = "clear_mobs"
    
    def func(self):
        # 搜索当前房间里名字以 DEBUG_MOB_ 开头的对象
        objs = [o for o in self.caller.location.contents if o.key.startswith("DEBUG_MOB_")]
        count = len(objs)
        for o in objs:
            o.delete()
        self.msg(f"已清理 {count} 个测试怪物。")


class PerformanceMonitor:
    """性能监控工具类"""
    def __init__(self):
        self.phases = []
        self.current_phase = None
        self.start_time = 0
        self.process = psutil.Process(os.getpid())
        
        # 获取初始状态
        self.start_io = self.process.io_counters()
        
        # DB文件路径
        self.db_path = settings.DATABASES['default']['NAME']
        self.wal_path = self.db_path + "-wal"

    def _get_db_size(self):
        """获取 DB + WAL 总大小"""
        size = 0
        if os.path.exists(self.db_path):
            size += os.path.getsize(self.db_path)
        if os.path.exists(self.wal_path):
            size += os.path.getsize(self.wal_path)
        return size / 1024 / 1024 # MB

    def start_phase(self, name):
        self.current_phase = name
        self.start_time = time.time()
        self.phase_start_io = self.process.io_counters()
        self.phase_start_db = self._get_db_size()

    def end_phase(self):
        duration = time.time() - self.start_time
        io_now = self.process.io_counters()
        
        # 计算增量
        write_bytes = io_now.write_bytes - self.phase_start_io.write_bytes
        # read_bytes = io_now.read_bytes - self.phase_start_io.read_bytes
        db_growth = self._get_db_size() - self.phase_start_db
        
        self.phases.append({
            'name': self.current_phase,
            'duration': duration,
            'write_mb': write_bytes / 1024 / 1024,
            'db_growth': db_growth
        })

    def get_report(self):
        """生成文本报告"""
        table = []
        table.append("\n" + "="*80)
        table.append(f"{'PHASE':<15} | {'TIME(s)':<8} | {'WRITE(MB)':<10} | {'DB+WAL(MB)':<10}")
        table.append("-" * 80)
        
        total_write = 0
        for p in self.phases:
            total_write += p['write_mb']
            table.append(f"{p['name']:<15} | {p['duration']:<8.2f} | {p['write_mb']:<10.4f} | {p['db_growth']:<+10.4f}")
            
        table.append("-" * 80)
        
        # 结论分析
        combat_phase = next((p for p in self.phases if p['name'] == 'Combat'), None)
        
        verdict = ""
        if combat_phase:
            if combat_phase['write_mb'] < 0.1:
                verdict = "|g[完美] 战斗阶段几乎无磁盘写入，全内存战斗生效！|n"
            else:
                verdict = "|r[失败] 战斗阶段发生写入，请检查属性同步机制。|n"
                
        table.append(verdict)
        table.append("="*80 + "\n")
        
        return "\n".join(table)