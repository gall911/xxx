"""
全自动命令加载器
功能：自动扫描当前文件夹下所有的 .py 文件，把里面的 Command 类全加载进来。
解放双手，再也不用手动 add 了！
"""
import psutil
import os
import importlib
import inspect
from evennia import CmdSet, Command
from django.conf import settings
from commands.dev.tb import CmdTestCombatDebug, CmdClearDebugMobs       
class DevCmdSet(CmdSet):
    """
    智能开发命令集
    """
    key = "DevCmdSet"
    priority = 1

    def at_cmdset_creation(self):
         # 2. 添加测试命令
        self.add(CmdTestCombatDebug)
        self.add(CmdClearDebugMobs)
        
        # 1. 获取当前脚本所在的文件夹路径 (commands/dev)
        current_dir = os.path.dirname(__file__)
        
        # 2. 定义包的路径前缀 (commands.dev)
        package_prefix = "commands.dev"
       
        
        # 3. 扫描文件夹里所有的文件
        for filename in os.listdir(current_dir):
            # 只处理 .py 文件，且忽略 __init__.py 和 自己 (dev_cmdset.py)
            if filename.endswith(".py") and not filename.startswith("__") and filename != "dev_cmdset.py":
                
                module_name = filename[:-3] # 去掉 .py 后缀
                full_module_path = f"{package_prefix}.{module_name}"
                
                try:
                    # 4. 动态导入模块 (相当于自动帮你写 from ... import ...)
                    mod = importlib.import_module(full_module_path)
                    
                    # 5. 检查模块里的每一个东西
                    for name, obj in inspect.getmembers(mod):
                        # 如果是类，且继承自 Command，且不是 Command 基类本身
                        if inspect.isclass(obj) and issubclass(obj, Command) and obj is not Command:
                            # 【关键】只加载定义在这个文件里的类
                            # (防止因为你在文件头 import 了 Command，导致重复加载基类)
                            if obj.__module__ == full_module_path:
                                try:
                                    self.add(obj())
                                    # print(f"自动加载: {name} (来自 {filename})")
                                except Exception as e:
                                    print(f"|r加载命令 {name} 失败: {e}|n")
                                    
                except Exception as e:
                    print(f"|r[自动加载] 跳过文件 {filename}: {e}|n")