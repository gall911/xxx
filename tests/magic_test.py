
# 测试魔法系统
import os
import sys

# 添加项目路径到系统路径
sys.path.insert(0, '/home/gg/xxx')

# 设置 Evennia 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.conf.settings')

# 初始化 Django
import django
django.setup()

# 导入必要的模块
from evennia.utils.create import create_object
from world.magic.spells.attack_spells.fire_spells import Fireball
from typeclasses.characters import Character
from world.magic.magic_system import get_magic_system

def test_fireball():
    """测试火球术"""
    print("开始测试火球术...")

    # 创建测试房间
    from typeclasses.rooms import Room
    room = create_object(Room, key="test_room")

    # 创建测试角色
    caster = create_object(Character, key="test_caster")
    target = create_object(Character, key="test_target")

    # 将角色移动到房间
    caster.location = room
    target.location = room

    # 设置角色属性
    caster.db.mana = 100
    caster.db.max_mana = 100
    caster.db.magic_power = 5
    caster.db.known_spells = ["fireball"]

    target.db.health = 100
    target.db.max_health = 100

    # 获取魔法系统
    print("获取魔法系统...")
    magic_system = get_magic_system()
    if not magic_system:
        print("无法获取魔法系统")
        return

    print("魔法系统初始化成功")

    # 注册火球术
    print("注册火球术...")
    fireball = create_object(Fireball, key="fireball")
    magic_system.register_spell(fireball)

    print("火球术注册成功")

    # 测试施法
    print("施放火球术...")
    success, message = magic_system.cast_spell(caster, "fireball", target)
    print(f"施法结果: {success}")
    print(f"消息: {message}")
    print(f"施法后法力: {caster.db.mana}")
    print(f"目标后生命值: {target.db.health}")

    # 清理测试对象
    caster.delete()
    target.delete()
    fireball.delete()

    print("测试完成!")

if __name__ == "__main__":
    test_fireball()
