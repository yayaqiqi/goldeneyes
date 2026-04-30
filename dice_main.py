import random
import re
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from dice.onedice import RD


def roll_dice(message,user_nickname=""):
    """处理骰子指令，返回投掷结果"""
    message = message.strip()

    # 忽略非骰子指令
    if not (message.startswith('.r') or message.startswith('．r')):
        return None

    # 去除前导点号
    if message.startswith('．'):
        message = '.' + message[1:]

    content = message[1:]  # 去掉点号

    # 解析指令类型和参数
    # .rd80 或 .r3d6 格式: r开头，后跟数字和可选的d骰子
    # .ra80 或 .ra 格式: a开头

    # 先检查 .ra 态度骰（更长的前缀先匹配）
    if content.startswith('ra'):
        # .ra80 或 .ra 格式 (态度骰)
        target = 50  # 默认50
        attr_name = ""

        after_ra = content[2:]  # 去掉ra
        if after_ra:
            # 检查是否包含属性名 + 数字，如"智力80"
            attr_match = re.match(r'^([^\d]+)(\d+)$', after_ra)
            if attr_match:
                attr_name = attr_match.group(1)
                target = int(attr_match.group(2))
            else:
                num_match = re.match(r'^(\d+)$', after_ra)
                if num_match:
                    target = int(num_match.group(1))
                else:
                    return None

        rd = RD("1d100")
        rd.roll()
        if rd.resError is not None:
            return f"骰子表达式错误：{rd.resError}"

        result = rd.resInt

        # 态度骰判定 - 根据难度判断
        if result == 1:
            judge = "✨ 大成功，自然选择，前进四！"
        elif result == 100:
            judge = "💥 大失败……这是计划的一部分。"
        elif result <= max(1, target // 5):
            judge = "🌟 极难成功，终一生渡世人，和终一世渡一人，都不如此刻投个成功。"
        elif result <= max(2, target // 2):
            judge = "✅ 困难成功，Mischeief Managed."
        elif result <= target:
            judge = "✅ 成功，I can do this all day."
        elif result >= 96:
            judge = "💀 大失败！一忘皆空。"
        elif result > target + (100 - target) // 5:
            judge = "❌ 困难失败，致我们鱼死网破的胜利。"
        elif result > target:
            judge = "⚠️ 失败，失去的东西到最后总会回到我们身边，虽然有时候出乎意料。"
        else:
            judge = "⚠️ 失败，失去的东西到最后总会回到我们身边，虽然有时候出乎意料。"

        attr_str = f"{attr_name}：" if attr_name else ""
        return f"🎲 [{user_nickname}] 乾坤一掷：{result} \n {judge}"

    elif content.startswith('rd'):
        # .rdN 格式 - 常规骰子
        sides_str = content[2:]
        if not sides_str.isdigit():
            return None
        sides = int(sides_str)
        expr = f"1d{sides}"

        rd = RD(expr)
        rd.roll()
        if rd.resError is not None:
            return f"骰子表达式错误：{rd.resError}"

        result = rd.resInt
        detail = rd.resDetail if rd.resDetail else str(result)
        return f"🎲 [{user_nickname}] 乾坤一掷：**{result}** *( {detail})*"

    elif content.startswith('r'):
        # .r3d6 格式 - 多骰常规骰
        rest = content[1:]  # 去掉r
        if 'd' in rest:
            idx = rest.index('d')
            count_str = rest[:idx]
            after_d = rest[idx+1:]
            if not count_str.isdigit():
                return None
            # 检查after_d是否包含+-修正
            mod_match = re.match(r'^(\d+)([+-]\d+)?$', after_d)
            if not mod_match:
                return None
            sides = int(mod_match.group(1))
            modifier = mod_match.group(2) or ""
            expr = f"{count_str}d{sides}{modifier}"

            rd = RD(expr)
            rd.roll()
            if rd.resError is not None:
                return f"骰子表达式错误：{rd.resError}"

            result = rd.resInt
            detail = rd.resDetail if rd.resDetail else str(result)
            return f"🎲 [{user_nickname}] 乾坤一掷：**{result}** *( {detail})*"

    return None
