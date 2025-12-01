import os
import re

def find_killers():
    print("正在扫描所有导致死锁的顶层引用...\n")
    
    # 我们要找的凶手特征：在顶层直接 import typeclasses
    patterns = [
        r"^from typeclasses\.[\w\.]+ import",
        r"^import typeclasses",
        r"^from typeclasses import"
    ]
    
    suspicious_files = []
    
    for root, dirs, files in os.walk("."):
        # 跳过虚拟环境和系统目录
        if "venv" in root or ".git" in root or "__pycache__" in root:
            continue
            
        for file in files:
            if not file.endswith(".py"):
                continue
                
            path = os.path.join(root, file)
            
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines):
                line = line.strip()
                # 检查是否匹配凶手特征
                for pat in patterns:
                    if re.search(pat, line):
                        # 排除掉我们在函数内部的 import (通常有缩进)
                        # 这里简单判断：如果 import 语句前面没有空格，那就是顶层引用！
                        original_line = lines[i]
                        if not original_line.startswith(" ") and not original_line.startswith("\t"):
                            print(f"🔴 发现凶手: {path}")
                            print(f"   第 {i+1} 行: {line}")
                            suspicious_files.append(path)
                            break
                            
    print("\n" + "="*50)
    if suspicious_files:
        print(f"共发现 {len(suspicious_files)} 个文件在顶层引用了 typeclasses。")
        print("这些文件会导致 Django 初始化死锁 (RuntimeWarning)。")
        print("请把这些文件里的 import 移到函数/方法内部！")
    else:
        print("太奇怪了，没有扫描到顶层引用。问题可能出在 typeclasses 目录内部的相互引用。")
    print("="*50)

if __name__ == "__main__":
    find_killers()