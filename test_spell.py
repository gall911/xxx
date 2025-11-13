
# 快速测试法术系统的脚本
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
    target.db.health = 100

    # 创建火球术对象
    fireball = create_object(Fireball, key="test_fireball")

    # 测试施法
    print(f"施法者法力: {caster.db.mana}")
    print(f"目标生命值: {target.db.health}")

    # 施放火球术
    success, message = fireball.cast(caster, target)

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
