import datetime
def calculate_hour_diff(time_str1, time_str2, floor=True):

    # 定义时间格式：YY-MM-DD HH:MM（注意%y是两位数年份，%Y是四位数）
    time_format = "%Y-%m-%d %H:%M"

    # 解析时间字符串为datetime对象
    time1 = datetime.datetime.strptime(time_str1, time_format)
    time2 = datetime.datetime.strptime(time_str2, time_format)

    # 计算时间差（秒数），取绝对值避免顺序问题
    time_diff_seconds = abs((time1 - time2).total_seconds())

    # 转换为小时（1小时=3600秒）
    hour_diff = time_diff_seconds / 3600

    # 向下取整（使用int()即可实现，因为正数向下取整等价于截断小数）
    if floor:
        hour_diff = int(hour_diff)

    return hour_diff

def calculate_now_how_diff(time_str1,floor=True):
    # 定义时间格式：YY-MM-DD HH:MM（注意%y是两位数年份，%Y是四位数）
    time_format = "%Y-%m-%d %H:%M"

    # 解析时间字符串为datetime对象
    time1 = datetime.datetime.strptime(time_str1, time_format)

    # 计算时间差（秒数），取绝对值避免顺序问题
    time_diff_seconds = abs((datetime.datetime.now()-time1).total_seconds())

    # 转换为小时（1小时=3600秒）
    hour_diff = time_diff_seconds / 3600

    # 向下取整（使用int()即可实现，因为正数向下取整等价于截断小数）
    if floor:
        hour_diff = int(hour_diff)

    return hour_diff



def calculate_now_hour_diff(time_str1,floor=True):

    # 定义时间格式：YY-MM-DD HH:MM（注意%y是两位数年份，%Y是四位数）
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    return calculate_hour_diff(time_str1,now,floor)

