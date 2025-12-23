# utils/gen_attrs.py

import sys
import os
import django

# ========================================================
# 1. 环境初始化
# ========================================================
GAME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, GAME_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.conf.settings")

try:
    django.setup()
except Exception as e:
    print(f"环境初始化失败: {e}")
    sys.exit(1)

from world.loaders.attr_loader import AttrLoader

# ========================================================
# 2. 配置与路径
# ========================================================
DOC_PATH = os.path.join(GAME_DIR, "docs", "attributes_guide.md")
CONST_PATH = os.path.join(GAME_DIR, "world", "const.py")

def get_padded_row(key, name, atype, default, desc, is_header=False):
    """
    核心辅助函数：生成强制对齐的表格行
    """
    # 定义每一列的宽度 (你可以根据需要调整)
    w_key = 25
    w_name = 12   # 中文占宽比较特殊，这里给宽一点
    w_type = 8
    w_def = 10
    w_desc = 40   # 描述最长

    # 截断超长的描述
    if len(desc) > w_desc - 3:
        desc = desc[:w_desc-3] + "..."

    # 格式化字符串
    # 屏幕打印和 md 文件通用这个格式
    row = f"| {key:<{w_key}} | {name:<{w_name}} | {atype:<{w_type}} | {str(default):<{w_def}} | {desc:<{w_desc}} |"
    
    return row

def generate_all():
    """主逻辑"""
    print(f"正在读取: {GAME_DIR}/data/attributes.yaml ...")
    data = AttrLoader.load_attrs(force_reload=True)
    
    if not data:
        print("未找到属性配置。")
        return

    # 准备表头
    header = get_padded_row("KEY (代码用)", "名称", "类型", "默认值", "描述 / 用途")
    # 分割线 (Markdown 格式)
    divider = f"|{'-'*27}|{'-'*14}|{'-'*10}|{'-'*12}|{'-'*42}|"

    # --- 1. 屏幕打印 (让你直接爽) ---
    print("\n" + "="*110)
    print(header)
    print(divider)

    rows = []
    
    for key in sorted(data.keys()):
        info = data[key]
        name = info.get('name', key)
        atype = info.get('type', 'str')
        default = info.get('default', info.get('base', '-'))
        desc = info.get('desc', '暂无')

        # 生成格式化行
        row_str = get_padded_row(key, name, atype, default, desc)
        rows.append(row_str)
        print(row_str) # 打印到屏幕

        # 如果是 gauge，额外加一行提示
        if atype == 'gauge':
            sub_row = get_padded_row(f"  ↳ max_{key}", f"{name}上限", "int", default, "(自动生成)")
            rows.append(sub_row)
            print(sub_row)

    print("="*110 + "\n")

    # --- 2. 生成对齐的 Markdown 文档 ---
    with open(DOC_PATH, 'w', encoding='utf-8') as f:
        f.write(f"# 角色属性字典\n\n")
        f.write(f"> 自动生成时间: {django.utils.timezone.now()}\n\n")
        f.write(header + "\n")
        f.write(divider + "\n")  # Markdown 表格必须有这行
        for r in rows:
            f.write(r + "\n")
            
    print(f"|g[成功]|n 文档已生成 (排版已修复): {DOC_PATH}")

    # --- 3. 生成代码常量表 (world/const.py) ---
    with open(CONST_PATH, 'w', encoding='utf-8') as f:
        f.write("# world/const.py\n")
        f.write("# 自动生成的属性常量表\nfrom enum import StrEnum\n\n") # Python 3.11+ 支持 StrEnum 更好用
        
        f.write("class At(StrEnum):\n")
        f.write("    \"\"\"属性常量映射表\"\"\"\n")
        
        for key in sorted(data.keys()):
            info = data[key]
            name = info.get('name', key)
            
            f.write(f"    # {name}\n")
            f.write(f"    {key.upper()} = \"{key}\"\n")
            
            if info.get('type') == 'gauge':
                f.write(f"    MAX_{key.upper()} = \"max_{key}\"\n")
            f.write("\n")
            
    print(f"|g[成功]|n 常量表已生成: {CONST_PATH}")

if __name__ == "__main__":
    generate_all()