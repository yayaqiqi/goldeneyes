import random
import re

def roll_dice(message):
    """处理骰子指令，返回投掷结果"""
    message = message.strip()

    # 匹配格式：.rdN 或 .raN (N为数字)
    match = re.match(r'^\.(\w)(\d+)$', message)
    if not match:
        return None

    dice_type = match.group(1).lower()
    sides = int(match.group(2))

    if sides <= 0:
        return "骰子面数必须大于0"

    result = random.randint(1, sides)

    if dice_type == 'r':
        # .rdN - 常规骰子
        return f"🎲 投掷 {sides} 面骰子\n结果：**{result}**"
    elif dice_type == 'a':
        # .raN - 暗示骰子(用于命运/态度等)
        if result == 1:
            return f"🎲 投掷 {sides} 面骰子\n结果：**{result}**\n💥 大失败！"
        elif result == sides:
            return f"🎲 投掷 {sides} 面骰子\n结果：**{result}**\n✨ 大成功！"
        else:
            return f"🎲 投掷 {sides} 面骰子\n结果：**{result}**"
    else:
        return None
