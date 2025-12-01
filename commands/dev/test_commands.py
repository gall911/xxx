"""
高级压力测试与性能剖析 - 修复版
"""
from evennia import Command, create_object
from evennia.utils import logger
from twisted.internet import reactor
import time
import os
import psutil
from django.conf import settings

# 1.【修正】根据你的实际路径修改导入
from world.managers.combat_manager import COMBAT_MANAGER
from typeclasses.npcs import NPC

class CmdStressTest(Command):
    """
    全自动战斗性能剖析器
    
    用法:
      xx test <NPC数量> <战斗秒数>
      
    示例:
      xx test 50 30    # 创建50个NPC，战斗30秒，然后自动清理并出报告
    """
    
    key = "xx test"
    aliases = ["xxtest"]
    locks = "cmd:all()"
    help_category = "开发"
    
    def func(self):
        # 参数解析
        if not self.args or len(self.args.split()) != 2:
            self.caller.msg("用法: xx test <NPC数量> <战斗秒数>")
            return
        
        try:
            self.npc_count = int(self.args.split()[0])
            self.duration = int(self.args.split()[1])
        except ValueError:
            self.caller.msg("参数必须是数字。")
            return

        # 初始化监控
        try:
            self.process = psutil.Process(os.getpid())
        except Exception as e:
            self.caller.msg(f"|r错误: 无法加载 psutil ({e})|n")
            return

        self.npcs = []
        self.metrics = {
            'create': {},
            'combat': {},
            'cleanup': {}
        }
        
        # 获取文件路径
        self.db_path = settings.DATABASES['default']['NAME']
        self.wal_path = f"{self.db_path}-wal"
        
        # 2.【修正】修复 LOG_FILE 报错
        # Evennia 只有 settings.LOG_DIR，我们需要手动拼接 server.log
        self.log_path = os.path.join(settings.LOG_DIR, 'server.log')
        
        self.caller.msg(f"|w=== 开始全自动性能测试 (NPC: {self.npc_count}, 持续: {self.duration}s) ===|n")
        self.caller.msg(f"监控目标文件:\n1. DB: {os.path.basename(self.db_path)}\n2. Log: {os.path.basename(self.log_path)}")

        # 启动流程：阶段一 [创建]
        reactor.callLater(0.1, self._phase_create)

    def _snapshot(self):
        """获取当前瞬间的系统状态快照"""
        # I/O 计数
        io = self.process.io_counters()
        
        # 文件大小 (如果文件不存在则为0)
        def get_size(path):
            return os.path.getsize(path) if os.path.exists(path) else 0

        # 计算 WAL 文件的总和
        db_total = get_size(self.db_path) + get_size(self.wal_path)

        return {
            'time': time.time(),
            'read_bytes': io.read_bytes,
            'write_bytes': io.write_bytes,
            'db_size': db_total,
            'log_size': get_size(self.log_path)
        }

    def _calc_diff(self, start, end):
        """计算两个快照之间的差值"""
        return {
            'duration': end['time'] - start['time'],
            'write_mb': (end['write_bytes'] - start['write_bytes']) / 1024 / 1024,
            'read_mb': (end['read_bytes'] - start['read_bytes']) / 1024 / 1024,
            'db_growth_mb': (end['db_size'] - start['db_size']) / 1024 / 1024,
            'log_growth_mb': (end['log_size'] - start['log_size']) / 1024 / 1024
        }

    # -------------------------------------------------------------------------
    # 阶段 1: 创建 NPC
    # -------------------------------------------------------------------------
    def _phase_create(self):
        self.caller.msg(f"\n|y[阶段 1/3] 正在创建 {self.npc_count} 个 NPC...|n")
        start_snap = self._snapshot()
        
        location = self.caller.location
        for i in range(self.npc_count):
            npc = create_object(
                NPC,
                key=f"T_NPC_{i}",
                location=location
            )
            # 极简初始化
            npc.ndb.hp = 10000 
            npc.ndb.max_hp = 10000
            npc.ndb.skills = ['普通攻击'] 
            self.npcs.append(npc)
            
        end_snap = self._snapshot()
        self.metrics['create'] = self._calc_diff(start_snap, end_snap)
        self.caller.msg(f"|g创建完成。耗时 {self.metrics['create']['duration']:.2f}s|n")
        
        # 休息1秒让数据库落盘
        reactor.callLater(1.0, self._phase_combat_start)

    # -------------------------------------------------------------------------
    # 阶段 2: 战斗循环
    # -------------------------------------------------------------------------
    def _phase_combat_start(self):
        self.caller.msg(f"\n|y[阶段 2/3] 启动战斗 (持续 {self.duration}s)...|n")
        
        # 启动战斗
        count = 0
        for i in range(0, len(self.npcs) - 1, 2):
            # 确保 COMBAT_MANAGER 可以正常调用
            if COMBAT_MANAGER.start_combat(self.npcs[i], self.npcs[i+1]):
                count += 1
        self.caller.msg(f"并发战斗组数: {count}")
        
        # 记录战斗开始时的状态
        self.combat_start_snap = self._snapshot()
        
        # 设置结束定时器
        reactor.callLater(self.duration, self._phase_combat_end)

    def _phase_combat_end(self):
        end_snap = self._snapshot()
        self.metrics['combat'] = self._calc_diff(self.combat_start_snap, end_snap)
        self.caller.msg(f"|g战斗测试结束。|n")
        
        # 停止管理器中的所有战斗
        for k in list(COMBAT_MANAGER.active_combats.keys()):
            COMBAT_MANAGER.stop_combat(k)
            
        # 进入清理
        reactor.callLater(0.5, self._phase_cleanup)

    # -------------------------------------------------------------------------
    # 阶段 3: 清理
    # -------------------------------------------------------------------------
    def _phase_cleanup(self):
        self.caller.msg(f"\n|y[阶段 3/3] 清理对象...|n")
        start_snap = self._snapshot()
        
        count = 0
        for npc in self.npcs:
            if npc and npc.pk:
                npc.delete()
                count += 1
                
        end_snap = self._snapshot()
        self.metrics['cleanup'] = self._calc_diff(start_snap, end_snap)
        
        # 打印最终报告
        self._print_report()

    # -------------------------------------------------------------------------
    # 生成报告
    # -------------------------------------------------------------------------
    def _print_report(self):
        m = self.metrics
        msg = "\n" + "="*60 + "\n"
        msg += f"|w性能剖析报告 (NPC: {self.npc_count})|n\n"
        msg += "="*60 + "\n"
        
        # 表头
        msg += f"{'阶段':<10} | {'耗时(s)':<8} | {'总写入(MB)':<10} | {'DB增长(MB)':<10} | {'Log增长(MB)':<10}\n"
        msg += "-"*60 + "\n"
        
        # 数据行
        def fmt_row(name, data):
            # 处理可能的 None 或 错误数据
            if not data: return f"{name:<10} | N/A"
            return (f"{name:<10} | {data['duration']:<8.2f} | "
                    f"{data['write_mb']:<10.2f} | {data['db_growth_mb']:<10.2f} | "
                    f"{data['log_growth_mb']:<10.2f}")

        msg += fmt_row("创建阶段", m.get('create')) + "\n"
        msg += fmt_row("战斗阶段", m.get('combat')) + "\n"
        msg += fmt_row("清理阶段", m.get('cleanup')) + "\n"
        
        msg += "-"*60 + "\n"
        
        # 结论分析
        try:
            total_write = m['create']['write_mb'] + m['combat']['write_mb'] + m['cleanup']['write_mb']
            msg += f"|w总磁盘写入:|n {total_write:.2f} MB\n"
            
            if m['create']['write_mb'] > m['combat']['write_mb']:
                msg += "|g分析:|n 写入主要发生在 [创建阶段]，这是正常的。\n"
            else:
                msg += "|r分析:|n 战斗阶段产生了大量写入！请检查 .db vs .ndb 使用情况。\n"
                
            if m['combat']['log_growth_mb'] > 0.5:
                 msg += "|y警告:|n 战斗过程产生了大量日志，建议关闭 DEBUG 日志。\n"
        except:
            msg += "数据不足，无法分析。\n"

        msg += "="*60
        self.caller.msg(msg)

class CmdIOMonitor(Command):
    """简单的IO监控开关（备用）"""
    key = "xx io"
    aliases = ["xxio"]
    locks = "cmd:all()"
    help_category = "开发"
    
    def func(self):
        self.caller.msg("请使用 'xx test' 进行全自动分析。")