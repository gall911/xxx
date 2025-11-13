from evennia import DefaultScript
import random

class MurenRegenScript(DefaultScript):
    """
    木人桩回血脚本 - 定期恢复木人桩的生命值
    """

    def at_script_creation(self):
        """创建脚本时的初始化"""
        self.key = "muren_regen_script"
        self.desc = "木人桩回血脚本"
        self.interval = 2  # 每2秒执行一次
        self.persistent = True
        self.start_delay = True  # 启动后延迟一段时间再开始

    def at_repeat(self):
        """脚本定期执行的内容"""
        obj = self.obj

        # 检查对象是否存在且未被摧毁
        if not obj or getattr(obj.db, 'is_destroyed', False):
            return

        # 获取当前HP和最大HP
        current_hp = getattr(obj.db, 'hp', 0)
        max_hp = getattr(obj.db, 'max_hp', 0)
        regen_rate = getattr(obj.db, 'regen_rate', 0)

        # 如果HP已满，无需恢复
        if current_hp >= max_hp:
            return

        # 计算新的HP值
        new_hp = min(current_hp + regen_rate, max_hp)

        # 更新HP
        obj.db.hp = new_hp

        # 如果HP从0恢复到大于0，显示特殊消息
        if current_hp == 0 and new_hp > 0:
            recover_message = getattr(obj.db, 'recover_from_zero_message', 
                                    f"{obj.key}开始自行修复，裂纹逐渐消失...")
            obj.location.msg_contents(recover_message.replace("{name}", obj.key))
        # 如果HP恢复到满值，显示消息
        elif new_hp == max_hp:
            full_recover_message = getattr(obj.db, 'full_recover_message', 
                                         f"{obj.key}已完全修复，看起来完好如初！")
            obj.location.msg_contents(full_recover_message.replace("{name}", obj.key))
