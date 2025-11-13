from evennia import Command
from evennia.utils.ansi import ANSIString
# 假设你的 theme 配置文件在 server.conf.theme
from server.conf.theme import (
    HP_BAR, MP_BAR, HP_SEPARATOR, HP_LABEL, 
    HP_VALUE, HP_GOLD, HP_SILVER
)

def make_bar(value, max_value, length=10, color_full="|g█|n", color_empty="|K░|n"):
    """
    生成带颜色的等长进度条。
    
    Args:
        value (int): 当前值.
        max_value (int): 最大值.
        length (int): 进度条的显示长度.
        color_full (str): 填充部分的ANSIString (例如: "|g█|n").
        color_empty (str): 空余部分的ANSIString (例如: "|K░|n").
        
    Returns:
        ANSIString: 格式化后的进度条.
    """
    value = max(0, min(value, max_value))
    
    if max_value <= 0:
        filled = 0
    else:
        filled = int(length * value / max_value)
        
    empty = length - filled
    
    # 组合并返回 ANSIString
    return ANSIString(f"{color_full * filled}{color_empty * empty}")

class CmdHp(Command):
    key = "hp"
    locks = "cmd:all()"
    help_category = "通用"

    def func(self):
        # 获取并处理属性
        db = self.caller.db
        hp = (db.hp or 0)
        max_hp = (db.max_hp or 1)
        mp = (db.mana or 0)
        max_mp = (db.max_mana or 1)
        cultivation = (db.cultivation or "未知")
        cultivation_level = (db.cultivation_level or 0)
        spirit_power = (db.spirit_power or 0)
        constitution = (db.constitution or 0)
        strength = (db.strength or 0)
        dexterity = (db.dexterity or 0)
        intelligence = (db.intelligence or 0)
        gold = (db.gold or 0)
        silver = (db.silver or 0)
        exp = (db.exp or 0)
        exp_needed = (db.exp_needed or 1)

        # --- 计算百分比和进度条 ---
        hp_percent = int(hp / max_hp * 100) if max_hp > 0 else 0
        mp_percent = int(mp / max_mp * 100) if max_mp > 0 else 0
        exp_percent = int(exp / exp_needed * 100) if exp_needed > 0 else 0

        hp_bar_color = "|r" if hp_percent < 30 else ("|310" if hp_percent < 70 else "|240")
        mp_bar_color = "|113" if mp_percent < 30 else ("|105" if mp_percent < 70 else "|015")

        # 优化：使用 xterm256 灰色 |238 作为"空"的颜色，比 |K 更美观
        empty_bar_color = "|=o|n"
        hp_bar = make_bar(hp, max_hp, 15, f"{hp_bar_color}█|n", empty_bar_color)
        mp_bar = make_bar(mp, max_mp, 15, f"{mp_bar_color}█|n", empty_bar_color)
        exp_bar = make_bar(exp, exp_needed, 10, "|c█|n", empty_bar_color)

        # --- 解决对齐问题的核心 ---
        
        # 优化：统一下 / 的对齐
        # {val:5} 表示右对齐，占5格
        hp_val_str = f"{hp:5}{HP_VALUE} / {max_hp:5}"
        mp_val_str = f"{mp:5}{HP_VALUE} / {max_mp:5}"
        
        # 优化：使用 ljust 保证左侧列的值填充到固定宽度
        # 这是解决 【灵力】/【力量】... 无法对齐的根本方法
        LEFT_VAL_WIDTH = 26 

        # 准备左侧的值，并使用 ljust 填充到固定宽度
        val_cult = ANSIString(f"{cultivation} ({cultivation_level})").ljust(LEFT_VAL_WIDTH)
        val_const = ANSIString(f"{constitution:5}").ljust(LEFT_VAL_WIDTH)
        val_dex = ANSIString(f"{dexterity:5}").ljust(LEFT_VAL_WIDTH)
        val_money = ANSIString(f"{HP_GOLD}{gold}{HP_VALUE}金 {HP_SILVER}{silver}{HP_VALUE}银").ljust(LEFT_VAL_WIDTH)

        # 准备右侧的值
        val_spirit = f"{spirit_power:5}"
        val_str = f"{strength:5}"
        val_int = f"{intelligence:5}"
        val_exp = f"{exp:5}/{exp_needed:5} ({exp_percent:3}%) {exp_bar}"

        # --- 构建显示文本 ---
        
        sep = f"{HP_SEPARATOR}≡{HP_VALUE}----------------------------------------------------------------{HP_SEPARATOR}≡{HP_VALUE}"
        
        # HP 和 MP 行 (使用上面准备好的 hp_val_str 和 mp_val_str)
        hp_line = f"{HP_LABEL}【 气 血 】{HP_VALUE} {HP_BAR}{hp_val_str} ({hp_percent:3}%) {hp_bar}"
        mp_line = f"{HP_LABEL}【 真 元 】{HP_VALUE} {MP_BAR}{mp_val_str} ({mp_percent:3}%) {mp_bar}"
        
        # 属性行 (使用上面准备好的, 已填充的 val_... 变量)
        line_cult = f"{HP_LABEL}【 境 界 】{HP_VALUE} {val_cult} {HP_LABEL}【 灵 力 】{HP_VALUE} {val_spirit}"
        line_const = f"{HP_LABEL}【 体 质 】{HP_VALUE} {val_const} {HP_LABEL}  【 力 量 】{HP_VALUE} {val_str}"
        line_dex = f"{HP_LABEL}【 敏 捷 】{HP_VALUE} {val_dex} {HP_LABEL}  【 智 力 】{HP_VALUE} {val_int}"
        line_money = f"{HP_LABEL}【 金 钱 】{HP_VALUE} {val_money} {HP_LABEL}【 经 验 】{HP_VALUE} {val_exp}"


        # 最终组合
        text = f"""
{HP_LABEL}> 你目前的状态属性如下：{HP_VALUE}
{sep}
{hp_line}
{mp_line}
{line_cult}
{line_const}
{line_dex}
{line_money}
{sep}"""

        self.msg(text)