from evennia import DefaultObject
import random
from utils.config_manager import game_config

class Muren(DefaultObject):
    """
    木人桩 - 可以快速回血，被攻击时会发出声音
    """

    def at_object_creation(self):
        """创建木人桩时初始化属性"""
        super().at_object_creation()

        # 默认使用基础木人桩配置
        self.db.dummy_type = "basic"
        self.db.is_destroyed = False

        # 从配置加载属性
        self.load_from_config()

        # 注册心跳脚本
        self.scripts.add("typeclasses.scripts.MurenRegenScript")

    def load_from_config(self):
        """从配置加载木人桩属性"""
        dummy_type = self.db.dummy_type or "basic"
        config = game_config.get_config("npcs/training_dummies")

        if not config or "training_dummies" not in config or dummy_type not in config["training_dummies"]:
            # 如果配置不存在，使用默认值
            self.db.desc = "一个坚实的木人桩，上面布满了练习留下的痕迹。"
            self.db.hp = 1000
            self.db.max_hp = 1000
            self.db.regen_rate = 50  # 每次心跳恢复50点HP
            self.db.rebuild_time = 5  # 被摧毁后重建时间（秒）

            # 设置默认的声音库
            self.db.hit_sounds = [
                "砰！",
                "啪！",
                "咚！",
                "咔嚓！",
                "砰砰！",
                "噼啪！",
                "咚咚！",
                "砰啪！",
                "咔！",
                "啪嗒！"
            ]

            # 设置默认的回应语句
            self.db.hit_responses = [
                "木屑四溅！",
                "木人桩震动了一下！",
                "木人桩发出沉闷的响声！",
                "木人桩摇晃了几下！",
                "木人桩上的裂纹又多了一道！",
                "木人桩微微颤抖！",
                "木人桩发出吱呀声！",
                "木人桩的表面凹陷了一块！"
            ]

            # 设置默认的特殊回应
            self.db.special_responses = [
                "{attacker}的攻击让木人桩剧烈摇晃！",
                "木屑从木人桩上飞溅而出！",
                "木人桩发出不堪重负的呻吟声！",
                "这一击似乎在木人桩上留下了新的痕迹！"
            ]

            # 设置默认的消息
            self.db.destroy_message = "{name}发出一声巨响，碎裂成了无数木屑！"
            self.db.rebuild_start_message = "{name}的碎片开始聚集，似乎要重新组合..."
            self.db.rebuild_complete_message = "{name}重新组合成形，恢复了原状！"
            self.db.recover_from_zero_message = "{name}开始自行修复，裂纹逐渐消失..."
            self.db.full_recover_message = "{name}已完全修复，看起来完好如初！"

            return

        # 从配置加载属性
        dummy_config = config["training_dummies"][dummy_type]

        # 设置基本属性
        self.db.desc = dummy_config.get("description", "一个坚实的木人桩，上面布满了练习留下的痕迹。")
        self.db.hp = dummy_config.get("hp", 1000)
        self.db.max_hp = dummy_config.get("max_hp", 1000)
        self.db.regen_rate = dummy_config.get("regen_rate", 50)  # 每次心跳恢复HP
        self.db.rebuild_time = dummy_config.get("rebuild_time", 5)  # 被摧毁后重建时间（秒）

        # 设置声音库
        self.db.hit_sounds = dummy_config.get("hit_sounds", [
            "砰！",
            "啪！",
            "咚！",
            "咔嚓！"
        ])

        # 设置回应语句
        self.db.hit_responses = dummy_config.get("hit_responses", [
            "木屑四溅！",
            "木人桩震动了一下！"
        ])

        # 设置特殊回应
        self.db.special_responses = dummy_config.get("special_responses", [
            "{attacker}的攻击让木人桩剧烈摇晃！"
        ])

        # 设置各种消息
        self.db.destroy_message = dummy_config.get("destroy_message", "{name}发出一声巨响，碎裂成了无数木屑！")
        self.db.rebuild_start_message = dummy_config.get("rebuild_start_message", "{name}的碎片开始聚集，似乎要重新组合...")
        self.db.rebuild_complete_message = dummy_config.get("rebuild_complete_message", "{name}重新组合成形，恢复了原状！")
        self.db.recover_from_zero_message = dummy_config.get("recover_from_zero_message", "{name}开始自行修复，裂纹逐渐消失...")
        self.db.full_recover_message = dummy_config.get("full_recover_message", "{name}已完全修复，看起来完好如初！")

        # 更新木人桩的名称
        if "name" in dummy_config:
            self.key = dummy_config["name"]

    def set_dummy_type(self, dummy_type):
        """设置木人桩类型"""
        self.db.dummy_type = dummy_type
        self.load_from_config()

    def at_hit(self, attacker=None, damage=None):
        """被击中时的反应"""
        if self.db.is_destroyed:
            return

        # 受到伤害
        if damage:
            self.db.hp = max(0, self.db.hp - damage)

            # 检查是否被摧毁
            if self.db.hp <= 0:
                self.destroy()
                return

        # 发出声音
        if self.db.hit_sounds:
            sound = random.choice(self.db.hit_sounds)
            self.location.msg_contents(f"{self.key}发出一声响亮的「{sound}」")

        # 显示回应
        if self.db.hit_responses:
            response = random.choice(self.db.hit_responses)
            self.location.msg_contents(response)

            # 偶尔显示特殊回应
            if random.random() < 0.2:  # 20%几率
                if self.db.special_responses:
                    special_response = random.choice(self.db.special_responses)
                    # 替换{attacker}为实际攻击者名称
                    if attacker:
                        special_response = special_response.replace("{attacker}", attacker.key)
                    else:
                        special_response = special_response.replace("{attacker}", "有人")
                    self.location.msg_contents(special_response)

    def destroy(self):
        """摧毁木人桩"""
        self.db.is_destroyed = True

        # 显示摧毁消息
        if self.db.destroy_message:
            message = self.db.destroy_message.replace("{name}", self.key)
            self.location.msg_contents(message)

        # 重建时间后重建
        import time
        from evennia import search_script
        from evennia.scripts.scripthandler import SCRIPT_DEFAULT

        # 创建一个延迟重建的脚本
        rebuild_script = search_script("typeclasses.scripts.MurenRebuildScript")
        if rebuild_script:
            rebuild_script = rebuild_script[0]
        else:
            rebuild_script = create_script("typeclasses.scripts.MurenRebuildScript")

        rebuild_script.db.muren_to_rebuild = self
        rebuild_script.start()

    def rebuild(self):
        """重建木人桩"""
        self.db.hp = self.db.max_hp
        self.db.is_destroyed = False

        # 显示重建完成消息
        if self.db.rebuild_complete_message:
            message = self.db.rebuild_complete_message.replace("{name}", self.key)
            self.location.msg_contents(message)
