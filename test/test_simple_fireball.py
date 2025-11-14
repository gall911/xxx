def simple_test():
    """
    最简火球术测试脚本
    """
    # 假设我们有一个角色对象caller
    caller = _test_get_caller()
    # 设置技能等级
    caller.db.skills = {
        "fire.fireball": {"level": 3}  # 3级火球术
    }
    # 创建一个测试目标 (100 HP)
    target = _test_create_target("测试木桩", 100)
    # 设置攻击目标
    caller.db.target = target
    # 执行cast命令
    from commands.cast import CmdCast
    cmd = CmdCast()
    cmd.caller = caller
    cmd.args = "fire.fireball"
    cmd.func()
    # 显示结果
    print(f"目标剩余HP: {target.db.hp}")
    # 清理
    _test_cleanup_target(target)

# 以下为测试辅助函数
def _test_get_caller():
    """模拟获取角色对象"""
    class TestCaller:
        def __init__(self):
            self.db = type('obj', (object,), {
                'skills': {},
                'target': None
            })()
            
        def msg(self, text):
            print(f"角色消息: {text}")
            
    return TestCaller()

def _test_create_target(name, hp):
    """创建测试目标"""
    class TestTarget:
        def __init__(self, name, hp):
            self.key = name
            self.db = type('obj', (object,), {
                'hp': hp
            })()
            
        def msg(self, text):
            print(f"目标消息: {text}")
            
    return TestTarget(name, hp)

def _test_cleanup_target(target):
    """清理测试目标"""
    print(f"清理目标: {target.key}")

if __name__ == "__main__":
    simple_test()