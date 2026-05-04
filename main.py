from sys import path
from turtle import goto
from khl import Bot, Message, MessageTypes, Event, EventTypes
from khl.card import Card, CardMessage, Module, Types, Element, Struct
import json
import logging
import datetime
import os
import shutil
import requests
import record as R
import template
import template as T
import utils
import dice_main
import random
import re

PATH = "./data/"

# logger set
logger = logging.getLogger("KOOK_Robot")
logger.setLevel(logging.INFO)
log_file = f"./logfile/mylog_{datetime.datetime.now().strftime('%Y%m%d')}.log"
file_handler = logging.FileHandler(log_file, encoding="utf-8")
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

SUCCESS = "✅ "
FAIL = "❌ "

def parse_kv(text, *keys):
    """按中文关键词链式解析文本，返回 {key: value} dict。
    示例: parse_kv(msg, "发信人：", "收信人：", "内容：")
    → {"发信人：": "发件人名", "收信人：": "收件人名", "内容：": "正文内容"}
    """
    result = {}
    remaining = text
    for i, key in enumerate(keys):
        if key not in remaining:
            raise ValueError(f"缺少关键词：{key}")
        if i == len(keys) - 1:
            result[key] = remaining.split(key, 1)[1].strip()
        else:
            next_key = keys[i + 1]
            result[key] = remaining.split(key, 1)[1].split(next_key, 1)[0].strip()
    return result

def loadData(name):
    filename = name + ".json"
    try:
        with open(PATH + filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        return True, data
    except FileNotFoundError as e:
        msg = f"操作失败：{e}"
        return False, msg

def setData(name, data):
    filename = name + ".json"
    try:
        with open(PATH + filename, "w", encoding="utf-8") as w:
            json.dump(data, w, indent=4, ensure_ascii=False)
        return True, "数据保存成功"
    except Exception as e:
        msg = f"操作失败：{e}"
        return False, msg

config_flag, config = loadData('config')
if not config_flag:
    print(f"启动失败：{config}")
    import sys; sys.exit(1)
bot = Bot(token=config['token'])
bk_header = {f'Authorization': f"Bot {config['token']}", f"Content-Type": f"application/json"}
url ="https://www.kookapp.cn/api"

@bot.task.add_cron(hour=12, minute=0, timezone="Asia/Shanghai")
async def auto_skin_notify_task():
    data = loadData('data')[1]
    guilds = data['guilds']
    # 每天清理删除频道
    for sName in guilds.values():
        deleteErrorChannel(sName)
        # timeoutEndPlay(sName)
        # remind(sName)


@bot.on_message()
async def handle_all_messages(msg: Message):
    if msg._channel_type != 'GROUP': return

    message = getMsgContent(msg)
    user_id = msg.author_id
    user_nickname = msg.author.nickname

    if message.startswith("创建·"):
        flag, rpl = createSeries(message, msg)
        await msg.reply(rpl)

    elif message.startswith("清空·"):
        name = message.replace("清空·", "").strip()
        flag, rpl = deleteSeries(name, PATH, msg.target_id)
        await msg.reply(rpl)
        if flag == 0: logger.error(rpl)

    elif message.startswith("绑定·"):
        flag, rpl = bindSolo(message,msg.target_id)
        await msg.reply(rpl)

    elif message.startswith("移除绑定·"):
        contents = message.replace("移除绑定·","").strip().split(" ")
        flag, rpl = removeSolo(contents,msg.target_id)
        await msg.reply(rpl)

    elif message.startswith("更改信息·"):
        rpl = updateSData(message)
        await msg.reply(rpl)

    elif message == "查看频道信息":
        rpl = getChannelInfo(msg.target_id)
        rpl_str = json.dumps(rpl, ensure_ascii=False, indent=4)
        await msg.reply(rpl_str)

    elif message.startswith(".") or message.startswith("．") or message.startswith("。"):
        rpl = dice_main.roll_dice(message,user_nickname)
        if rpl:
            await msg.reply(rpl)

    elif message.startswith("通讯·"):
        contents = message.replace("通讯·","").strip()
        flag,rpl = createChat(contents,msg.target_id)
        if not flag: await msg.reply(rpl)

    elif message.startswith("创建频道·"):
        rpl = createEPChannels(message, msg)
        await msg.reply(rpl)

    elif message.startswith("私约·"):
        flag, rpl = inviteMinidate(message,msg)
        await msg.reply(rpl)

    elif message.startswith("To"):
        flag, target_id, rpl = noteTo(message,msg.target_id)
        if flag: await msg.reply(rpl)

    elif message.startswith("礼物·"):
        f,r = sendGift(message,msg)
        await msg.reply(r)
    elif message.startswith("点歌台"):
        f,r = orderMusic(message,msg)
        await msg.reply(r)

    elif message.startswith("公共留言"):
        f,r = publicNote(message,msg)
        await msg.reply(r)

    elif message.startswith("心愿·"):
        rpl = publicWish(message,msg.target_id)
        await msg.reply(rpl)

    elif message.startswith("踩点·"):
        rpl = sendCaidian(message, msg)
        await msg.reply(rpl)

    elif message == "查看踩点信息":
        rpl = getCaidianInfo(msg.target_id)
        await msg.reply(rpl)

    elif message.startswith("心动信"):
        rpl = sendLetters(message,msg)
        await msg.reply(rpl)

    elif message=="撤回心动信":
        rpl = withdrawLetters(msg)
        await msg.reply(rpl)

    elif message == "发送心动信123":
        systemSendLetters(msg)

    elif message.startswith("添加记录·"):
        sData = getsDataJsonByChannelId(msg.target_id)
        channel_name = msg.ctx.channel.name.strip()
        name_list = channel_name[3:].strip().split("&")
        EP = message.replace("添加记录·","").strip()
        createRecord(sData['sName'],name_list,name_list[0],EP,msg.target_id,channel_name)
        await msg.reply(SUCCESS + "添加成功")


    elif message == "test12":
        await msg.reply("测试成功123")
        pass  # debug

    elif message == "个人档案":
        reply_msg = myPlayCheck(msg.target_id)
        await msg.reply(reply_msg)

    elif message == "回戏档案":
        reply_msg = unFinishedPlayCheck(msg.target_id)
        await msg.reply(reply_msg)

    elif message == "导出记录":
        await exportChannelRecord(msg)

    elif message == "结束对戏":
        endPlay(msg.target_id)


    elif message == "更新记录":
        updatePlayRecordByChannelId(msg.target_id,msg)
        await msg.reply(SUCCESS + "记录已更新")

    elif message.startswith("修正删除频道·"):
        sName = message.replace("修正删除频道·","").strip()
        rpl = deleteErrorChannel(sName)
        await msg.reply(rpl)

    elif message.startswith("检查超时·"):
        sName = message.replace("检查超时·","").strip()
        rpl = timeoutEndPlay(sName)
        await msg.reply(rpl)

    elif message.startswith("提醒回戏·"):
        sName = message.replace("提醒回戏·","").strip()
        rpl = remind(sName)
        await msg.reply(rpl)

    elif message.startswith("添加管理员·"):
        rpl = addAdmin(message, msg)
        await msg.reply(rpl)

    elif message.startswith("移除管理员·"):
        rpl = removeAdmin(message, msg)
        await msg.reply(rpl)

    elif message == "统计":
        rpl = getStatistics(msg)
        await msg.reply(rpl)

    elif message.startswith("折手指·"):
        rpl = await handleFingerGame(message, msg)
        await msg.reply(rpl)

    elif message.startswith("国王游戏出题·"):
        rpl = kingGameAssign(message, msg)
        await msg.reply(rpl)

    elif message.startswith("生成戏录·"):
        content = message.replace("生成戏录·","").strip()
        try:
            contents = content.split(" ")
            sName,pName = contents[0],contents[1]
        except Exception as e:
            logger.error(e)
            await msg.reply(FAIL + "操作失败，指令：生成戏录·恋综名称 玩家名称")
            return

        JSON_PATH = PATH + sName + "/" + pName + ".json"
        OUTPUT_HTML = PATH + sName + "/戏录_" + pName + ".html"
        rpl = R.generateRecord(JSON_PATH,OUTPUT_HTML)

        file_url = await bot.client.create_asset(OUTPUT_HTML)  # 上传测试文件
        # 卡片消息中的文件
        cm = CardMessage(Card(
            Module.Header(f"{pName} · 个人戏录文件"),
            Module.File(type="file", src=file_url, title='戏录文件.html')
        ))
        await msg.reply(cm)
        # await msg.reply(file_url, type=MessageTypes.FILE)
        await msg.reply(rpl)
    
    elif message.startswith("进入EP："):
        rpl = gotoEP(message,msg)
        await msg.reply(rpl)


    else:
        first_line = message.split("\n",1)[0].strip()
        info = getChannelInfo(msg.target_id)
        sData = loadData(info['guild_name'])[1]
        names = sData['solos'].keys()
        if first_line in names:
            playedUpdatedRecord(message,msg)



@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def handle_all_events(msg:Message, e:Event):
    pass  # debug
    message = e.extra['body']['value']
    msg_id = e.extra['body']['msg_id']
    target_id = e.extra['body']['target_id']
    user_nickname = e.extra['body']['user_info']['nickname']
    user_nickname = user_nickname.strip()

    ch = await bot.client.fetch_public_channel(target_id) # 获取频道

    if message.startswith("接受私约·"):
        flag,rpl = acceptMinidate(message,target_id,msg_id)
        if not flag:
              # 获取频道
            await ch.send(rpl, quote=msg_id)
            await ch.send("接受私约操作失败，请联系管理员", quote=msg_id)


    elif message.startswith("拒绝私约·"):
        flag,rpl = rejectMinidate(message,target_id,msg_id)
        await ch.send(rpl, quote=msg_id)

    elif message.startswith("心愿·"):
        flag, rpl = goWish(message, channel_id=target_id,recever_name=user_nickname,msg_id=msg_id)

    elif message.startswith("踩点选择"):
        rpl = selectCaidian(message, user_nickname,target_id)


def gotoEP(message,msg):

    EP = message.split("进入EP：",1)[1].strip()

    info = getsDataJsonByChannelId(msg.target_id)
    info['current_EP'] = EP
    setData(info['sName'],info)
    
    return SUCCESS + f"设置 [{EP}] 成功"

def addRecordCounts(message,channel_id,sName):
    name = message.split("\n",1)[0].strip()
    cnt = len(message)
    data = readRecord(sName,name)
    data['details'][channel_id]['counts'] += cnt
    saveRecord(sName,name,data)



def orderMusic(message,msg):

    try:
        sender = message.split("点歌人：",1)[1].split("收听者：",1)[0].strip()
        receiver = message.split("收听者：",1)[1].split("时间：",1)[0].strip()
        time = message.split("时间：",1)[1].split("留言：",1)[0].strip()
        note = message.split("留言：",1)[1].split("歌曲：",1)[0].strip()
        music = message.split("歌曲：",1)[1].strip()

        if note == "" or sender == "" or receiver == "" or time == "" or music == "":
            return False, FAIL + "内容不得为空\n"  + template.ORDER_MUSIC

        c = template.getMusicTemplate(note,sender,receiver,time)
        info = getsDataJsonByChannelId(msg.target_id)
        music_channel_id = info['public_channels'][template.KEY_MUSIC]
        sendMessage(music_channel_id,c,10)
        sendMessage(music_channel_id,music,9)

        return True,SUCCESS + "发送成功！"

    except Exception as e:
        logger.error(e)
        return False, template.ORDER_MUSIC

def sendLetters(message,msg):
    """心动信
    发信人：
    收信人：
    内容：
    """
    sData = getsDataJsonByChannelId(msg.target_id)
    sender = msg.ctx.channel.name

    # if not isAdmin(msg.author_id, sData):
    #     return FAIL + "没有权限，需要管理员权限才能执行此操作"
    logger.info(f"SendLeter: message={message}")
    if ("收信人：" in message
            and "发信人：" in message
            and "内容：" in message):
        # try:
        parts = parse_kv(message, "发信人：", "收信人：", "内容：")
        sender_name = parts["发信人："]
        recever_name = parts["收信人："]
        content = parts["内容："]

        names = sData['solos'].keys()
        if recever_name not in names:
            return FAIL + "收信人错误，请检查格式后重新输入！"

        letter_data = loadData(f"{sData['sName']}letter")[1]
        if sender not in letter_data.keys():letter_data[sender] = []
        imgs = []
        if msg.type == 10:
            imgs = getImgSrcsFromCardMessage(msg)

        letter = {
            'sender_name':sender_name,
            'recever_name':recever_name,
            'content':content,
            'imgs': imgs
        }

        #

        letter_data[sender].append(letter)
        setData(f"{sData['sName']}letter",letter_data)
        return SUCCESS + "心动信已收录"


        # except Exception as e:
        #     logger.error(e)
        #     return "格式错误，请按照以下格式发送心动信\n" + T.LETTER


    else:
        return "格式错误，请按照以下格式发送心动信\n" + T.LETTER

def withdrawLetters(msg):

    sender = msg.ctx.channel.name
    sData = getsDataJsonByChannelId(msg.target_id)
    letter_file_name = sData['sName']+"letter"

    d = loadData(letter_file_name)[1]
    d[sender] = []
    setData(letter_file_name,d)

    return SUCCESS + "心动信撤回成功"


def myPlayCheck(channel_id):

    sData = getsDataJsonByChannelId(channel_id)
    sName = sData['sName']
    pName = [k for k, v in sData['solos'].items() if v == channel_id][0]
    pData = readRecord(sName, pName)

    details = pData['details']
    counts = 0
    rpl = f"Hi, {pName}, 你在 [{sName}] 的个人记录如下：\n\n"

    groups = {
        "EP0": "",
        "EP1":"",
        "EP2": "",
        "EP3": "",
        "EP4": "",
        "EP5": ""
    }

    for key in details.keys():
        value = details[key]
        counts += value['counts']
        rounds = len(value['content'])
        if rounds % 2 == 0:
            msg_round = f"{int(rounds / 2)}v{int(rounds / 2)}"
        else:
            msg_round = f"{int(rounds // 2 + 1)}v{int(rounds // 2)}"

        if value['is_finished'] == 1:
            line ="\t" + SUCCESS + f" {value['channel_name']}: (chn){key}(chn) *{msg_round}* \n"

        else:
            time = utils.calculate_now_hour_diff(value['last_time'])
            if time <= 24:
                logo = "🟢 "
            elif time <= 48:
                logo = "🟡 "
            else:
                logo = "🔴 "

            if value['current_person'] == pName:
                line ="\t" +  f"{logo} 等你回戏，{value['channel_name']}: (chn){key}(chn) ({time}h)  *{msg_round}*\n"
                # wait_you = wait_you + line
            else:
                line ="\t" +  f"🕧  等待对方回戏，{value['channel_name']}: (chn){key}(chn) ({time}h)  *{msg_round}*\n"

        groups[value['EP']] += line

    for ep in groups.keys():
        if groups[ep]!= "":
            rpl = rpl +"**"+ ep + "**\n" + groups[ep] + "\n"

    reply = rpl + "\n" + f"当前共结戏 {pData['finished']} 个, 已写 {counts} 字 ❤。"
    return reply

def unFinishedPlayCheck(channel_id):
    sData = getsDataJsonByChannelId(channel_id)
    sName = sData['sName']
    pName = [k for k, v in sData['solos'].items() if v == channel_id][0]
    pData = readRecord(sName, pName)

    details = pData['details']
    rpl = f"Hi, {pName}, 你在 [{sName}] 未结束的对戏如下：\n\n"

    groups = {
        "EP0": "",
        "EP1": "",
        "EP2": "",
        "EP3": "",
        "EP4": "",
        "EP5": ""
    }

    for key in details.keys():
        value = details[key]
        if value['is_finished'] == 1:
            continue  # 跳过已完成的

        rounds = len(value['content'])
        if rounds % 2 == 0:
            msg_round = f"{int(rounds / 2)}v{int(rounds / 2)}"
        else:
            msg_round = f"{int(rounds // 2 + 1)}v{int(rounds // 2)}"

        time = utils.calculate_now_hour_diff(value['last_time'])
        if time <= 24:
            logo = "🟢 "
        elif time <= 48:
            logo = "🟡 "
        else:
            logo = "🔴 "

        if value['current_person'] == pName:
            line = "\t" + f"{logo} 等你回戏，{value['channel_name']}: (chn){key}(chn) ({time}h)  *{msg_round}*\n"
        else:
            line = "\t" + f"🕧  等待对方回戏，{value['channel_name']}: (chn){key}(chn) ({time}h)  *{msg_round}*\n"

        groups[value['EP']] += line

    has_unfinished = False
    for ep in groups.keys():
        if groups[ep] != "":
            has_unfinished = True
            rpl = rpl + "**" + ep + "**\n" + groups[ep] + "\n"

    if not has_unfinished:
        return SUCCESS + "所有对戏都清啦~"

    return rpl

def kingGameAssign(message, msg):
    """国王游戏出题：数字和字母组人名随机对应后替换题目"""
    content = message.strip()

    lines = content.split("\n")
    first_line = lines[0].strip()

    if not first_line.startswith("国王游戏出题·"):
        return FAIL + "格式错误，指令：国王游戏出题·人数\n数字：角色A、角色B……\n字母：角色A、角色B……\n题目内容"

    try:
        count = int(first_line.split("·", 1)[1])
    except:
        return FAIL + "人数格式错误"

    numbers = {}
    letters = {}
    questions = []

    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue

        if "数字：" in line:
            num_part = line.split("数字：", 1)[1].strip()
            names = [n.strip() for n in num_part.split("、") if n.strip()]
            for i, name in enumerate(names[:count]):
                numbers[str(i + 1)] = name
        elif "字母：" in line:
            letter_part = line.split("字母：", 1)[1].strip()
            names = [n.strip() for n in letter_part.split("、") if n.strip()]
            for i, name in enumerate(names[:count]):
                letters[chr(65 + i)] = name
        elif line:
            questions.append(line)

    if len(numbers) < count or len(letters) < count:
        return FAIL + f"嘉宾人数与题目设置人数不匹配"

    num_names = list(numbers.values())
    letter_names = list(letters.values())
    random.shuffle(letter_names)
    random.shuffle(num_names)

    num_to_name = {str(i + 1): num_names[i] for i in range(count)}
    letter_to_name = {chr(65 + i): letter_names[i] for i in range(count)}

    mapping_output = ["**数字对应：**"]
    for i in range(count):
        mapping_output.append(f"{i + 1} → {num_names[i]}")

    mapping_output.append("\n**字母对应：**")
    for i in range(count):
        mapping_output.append(f"{chr(65 + i)} → {letter_names[i]}")

    mapping_output.append("\n**题目匹配结果：**")
    sData = getsDataJsonByChannelId(msg.target_id)
    try:
    
        for q in questions:
            q_text = q
            for num, name in num_to_name.items():
                user_id = sData['user_ids'].get(name, '')
                q_text = replace_placeholder(q_text, num, f'(met){user_id}(met)')
            for letter, name in letter_to_name.items():
                user_id = sData['user_ids'].get(name, '')
                q_text = replace_placeholder(q_text, letter, f'(met){user_id}(met)')
            mapping_output.append(q_text)
    except:
        return FAIL + "请检查嘉宾姓名是否正确"

    return "\n".join(mapping_output)

import re

# 替换时确保前后不是字母或数字
def replace_placeholder(text, placeholder, replacement):
    # 匹配前后有边界的占位符
    pattern = rf'(?<![a-zA-Z0-9]){re.escape(placeholder)}(?![a-zA-Z0-9])'
    return re.sub(pattern, replacement, text)


def deleteErrorChannel(sName):
    sData = loadData(sName)[1]
    names = sData['solos']
    for name in names:
        precord = readRecord(sName,name)
        delete_channels = []
        channels = list(precord['details'].keys())
        for channel_id in channels:
            response = getChannel(channel_id)
            if response['code'] == 400:
                precord['details'].pop(channel_id)

        saveRecord(sName,name,precord)
    return SUCCESS + "修正完成"

def timeoutEndPlay(sName):
    sData = loadData(sName)[1]
    names = sData['solos']
    rpl_list = []
    for name in names:
        precord = readRecord(sName,name)
        channels = precord['details'].keys()
        for channel_id in channels:
            info = precord['details'][channel_id]
            time = info['last_time']
            diff = utils.calculate_now_hour_diff(time)
            if diff > 72 and info['is_finished']==0:
                rpl_list.append(f"{info['EP']} (chn){channel_id}(chn) 已超时，强结。")
                endPlay(channel_id)
    return SUCCESS + "执行完成\n" + "\n".join(rpl_list)

def remind(sName):
    sData = loadData(sName)[1]
    names = sData['solos']

    remind_list = []
    for name in names:
        precord = readRecord(sName,name)
        channels = precord['details'].keys()
        for channel_id in channels:
            info = precord['details'][channel_id]
            if info['is_finished'] == 1 or name != info['current_person']: continue
            time = info['last_time']
            diff = utils.calculate_now_hour_diff(time)
            if diff >= 24:
                latest_msg = getLatestMessage(channel_id)[0]
                if len(latest_msg['mention']) > 0:
                    last_mention_time = latest_msg['create_at']
                    diff_latest_mention = utils.calculate_now_hour_diff_by_timestamp(last_mention_time)
                    if diff_latest_mention > 12:
                        sendMessage(channel_id,f"(met){sData['user_ids'][name]}(met)",9)
                remind_list.append(f"{info['EP']} (chn){channel_id}(chn) 已提醒,*{name} ({diff}h)*")
                    
    return SUCCESS + "提醒完成，12小时内提醒过不会重复提醒。\n" + "\n".join(remind_list)

def endPlay(channel_id):
    info = getChannelInfo(channel_id)
    c_name = info['name']
    names = c_name[3:].split("&")
    sName = info['guild_name']
    reply_msg = SUCCESS + "记录已更新\n"
    flag = False
    updatePlayRecordByChannelId(channel_id)
    for name in names:
        pdata = readRecord(sName,name)
        flag = pdata['details'][channel_id]['is_finished']
        if flag == 1: continue
        else:
            flag = True
            pdata['details'][channel_id]['is_finished'] = 1
            pdata['finished'] += 1
            saveRecord(sName,name,pdata)
    if flag:
        sendMessage(channel_id,reply_msg,9)
        sendMessage(channel_id,"————— **END** ————",9)
    return

# 根据指令更新频道
def updatePlayRecordByChannelId(channel_id,msg=None):
    # 获取这个频道的所有消息

    mlist = getChannelMessageList(channel_id)
    if msg==None:
        names = getChannelInfo(channel_id)['name'][3:].split("&")
    else:
        names = msg.ctx.channel.name[3:].split("&")
    sData = getsDataJsonByChannelId(channel_id)
    sName = sData['sName']
    
    for name in names:
        precord = readRecord(sName,name)
        precord['details'][channel_id]['content'] = []
        precord['details'][channel_id]['counts'] = 0
        saveRecord(sName,name,precord)

    # 遍历录入
    for m in mlist:
        content = m['content']
        fline = content.split("\n",1)[0].strip()
        if fline in sData['solos'].keys():
            playedUpdatedRecord(content,msg=None,channel_id = channel_id)

def playedUpdatedRecord(message, msg=None,channel_id=None):
    first_line = message.split("\n", 1)[0].strip()
    if msg!=None:
        channel_id = msg.target_id
    info = getChannelInfo(channel_id)
    sData = loadData(info['guild_name'])[1]
    # names = sData['solos'].keys()
    channel_name = info['name'].strip()
    persons = channel_name[3:].split("&")

    # 更新个人档案
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    for i in range(len(persons)):
        if first_line == persons[i]:
            current_person = persons[(i + 1) % len(persons)]
            break;
    # 更新字数
    addRecordCounts(message, channel_id, sData['sName'])

    for pname in persons:
        pdata = readRecord(sData['sName'], pname)
        pdata['details'][channel_id]['last_time'] = now
        pdata['details'][channel_id]['current_person'] = current_person
        pdata['details'][channel_id]['content'].append(message)
        saveRecord(sData['sName'], pname, pdata)
        logger.info(f"updated [{pname}]!")

def getMsgContent(msg):
    message = "Message Type Not 9 and 10"
    if msg.type == 9:
        message = msg.content
    elif msg.type == 10:
        # 获取文字
        contents = json.loads(msg.content)[0]['modules'][0]
        if contents['type'] == 'section':
            message = contents['text']['content']
        else:
            return False

    return message

def createSeries(message,msg):
    name = message.replace("创建·", "").strip()

    if len(name)==0 or len(name)>=10 :
        return False,FAIL + "创建失败，恋综名称不能为空或过长！格式:创建·恋综名称"

    filename =f"{name}.json"



    full_file_path = PATH + filename
    os.makedirs(PATH + "/" + name, exist_ok=True)
    if os.path.exists(full_file_path):
        return False,FAIL +  f"创建失败，{filename}已存在，避免重复创建！请先清空旧文件再创建。清空格式：清空·恋综名称"

    info = getChannelInfoNotRegisted(msg.target_id)
    guild_id = info['guild_id']

    with open(full_file_path, 'w', encoding='utf-8') as f:
        data = {
            "sName": name.strip(),
            "guild_id": guild_id,
            "current_EP":"EP0",
            "admins":["2885606149"],
            "solos":{},
            "roles":{},
            "parents":{},
            "user_ids":{},
            "admins": [msg.author_id]
        }
        json.dump(data, f, indent=4, ensure_ascii=False)

    with open(PATH + "/" + name + "letter.json", 'w', encoding='utf-8') as f:
        json.dump({}, f, ensure_ascii=False)

    flag, data = loadData("data")
    if not flag: return flag,data
    if guild_id in data['guilds'].keys(): return False, f"创建失败，当前guild_id:[{guild_id}]已绑定"
    data['guilds'][guild_id] = name
    flag,msg = setData('data', data)
    if flag: return True,SUCCESS + f"恋综 [{name}] 创建成功"
    return flag,msg


def getChannelInfo(channel_id):

    params = {
        "target_id":channel_id
    }
    response = requests.get(url + "/v3/channel/view", headers=bk_header,params=params)
    msg = json.loads(response.text)
    msg = msg['data']
    guild_name = loadData('data')[1]['guilds'][msg['guild_id']]
    rpl = {
        'id':msg['id'],
        'guild_id':msg['guild_id'],
        'guild_name':guild_name,
        'parent_id':msg['parent_id'],
        'name':msg['name']
    }
    return rpl

def getChannelListByParentId(guild_id,parent_id):
    params = {
        "guild_id":guild_id,
        "parent_id":parent_id
    }
    response = requests.get(url + "/v3/channel/list", headers=bk_header,params=params)
    msg = json.loads(response.text)
    try:
        r = msg['data']['items']
    except:
        logger.error(msg)
        r = []
    return r

def getChannel(channel_id):
    params = {
        "target_id":channel_id
    }
    response = requests.get(url + "/v3/channel/view", headers=bk_header,params=params)
    msg = json.loads(response.text)
    return msg


def getChannelInfoNotRegisted(channel_id):
    params = {
        "target_id":channel_id
    }
    response = requests.get(url + "/v3/channel/view", headers=bk_header,params=params)
    msg = json.loads(response.text)
    msg = msg['data']
    rpl = {
        'id':msg['id'],
        'guild_id':msg['guild_id'],
        'parent_id':msg['parent_id'],
        'name':msg['name']
    }
    return rpl

def deleteSeries(name,path,channel_id):
    if len(name.strip())==0:
        return False,FAIL + "清空失败，恋综名称不能为空！格式:清空·恋综名称"

    filename =f"{name.strip()}.json"
    full_file_path = path + filename
    if not os.path.exists(full_file_path):
        return False,FAIL +  f"清空失败，{filename}不存在，无需清空"

        # 5. 创建JSON文件（写入空JSON对象）
    try:
        os.remove(full_file_path)
        os.remove(path + name + "letter.json")
        info = getChannelInfo(channel_id)
        guild_id = info['guild_id']

        flag, data = loadData("data")
        if not flag: return flag, data
        if guild_id in data['guilds'].keys():
            data['guilds'].pop(guild_id)

        setData('data',data)
        return True,SUCCESS + f"恋综 [{name.strip()}] 已清空"


    except Exception as e:
        return False,FAIL + f"操作失败:{e}"

def bindSolo(message,group_id):
    contents = message.replace("绑定·", "").strip().split(" ")
    logger.info(contents)
    if len(contents) != 4:
        return False, FAIL + f"操作失败，请检查信息之间是否有超过1个空格。个人频道绑定格式：绑定·恋综名称 角色名称 @玩家账号 @角色组"

    try:
        sName, pName,user_id,role_id = contents[0], contents[1].strip(),contents[2].strip(), contents[3].strip()
    except Exception as e:
        msg = FAIL + f"操作失败，个人频道绑定格式：绑定·恋综名称 角色名称 @玩家账号 @角色组"
        logger.info(msg)
        return False, msg

    flag, sData = loadData(sName)
    if not flag: return flag, sData

    if pName in sData['solos'].keys():
        return False, FAIL + "绑定失败，代号词已重复"
    elif group_id in sData['solos'].values():
        return False,FAIL + "绑定失败，当前频道已绑定，若续更换绑定词，格式：移除绑定·恋综。"
    
    if "met" not in user_id or "rol" not in role_id:
        return False, FAIL + f"操作失败，玩家账号或角色组识别错误"

    user_id = user_id.strip().replace("(met)", "")
    role_id = role_id.strip().replace("(rol)", "")

    if "@" in user_id or "@" in role_id:
        return False, FAIL + f"操作失败，个人频道绑定格式：绑定·恋综名称 角色名称 @玩家账号 @角色组"

    sData['solos'][pName] = group_id
    sData['roles'][pName] = role_id
    sData['user_ids'][pName] = user_id
    flag, msg = setData(sName,sData)
    if flag: msg = SUCCESS + f"{sName}·{pName} 个人频道绑定成功"

    #创建个人档案
    person_file = PATH + f"/{sName}/{pName}.json"
    with open(person_file, 'w', encoding='utf-8') as f:
        pdata = {
            "name": pName,
            "sName": sName,
            "finished":0,
            "groups":0,
            "details":{}
        }
        json.dump(pdata, f, indent=4, ensure_ascii=False)

    return flag,msg

def removeSolo(contents,group_id):
    try:
        sName = contents[0]
    except Exception as e:
        msg = FAIL + f"操作失败，个人频道移除绑定格式：移除绑定·恋综名称"
        logger.info(msg)
        return False,msg

    flag, sData = loadData(sName)
    if not flag: return flag, sData

    if "solos" not in sData.keys():
        sData['solos'] = {}

    remove_name = ""
    for key in list(sData['solos'].keys()):
        if sData['solos'][key] == group_id:
            remove_name = key
            del sData['solos'][key]
            break

    if remove_name!="":
        sData['roles'].pop(remove_name)
        sData['user_ids'].pop(remove_name)

    flag, msg = setData(sName, sData)
    if flag: msg = SUCCESS + f"当前频道绑定解除成功"
    return flag, msg

def updateChannelRole(channel_id,role_id):

    payload = {
        "channel_id":channel_id,
        "type":"role_id",
        "value": role_id,
        "allow": 2048,
        "deny": 0
    }
    response = requests.post(url + '/v3/channel-role/update', headers=bk_header, json=payload)
    logger.info(json.loads(response.text))
    return

def createChat(content,channel_id):
    names = content.strip().split("&")
    if len(names)<=1 :
        return False,FAIL +  "通讯创建失败，格式错误！格式:通讯·角色名称&角色名称"

    info = getChannelInfo(channel_id)
    sName = loadData("data")[1]['guilds'][info['guild_id']]
    sData = loadData(sName)[1]

    parent_id = sData['parents']['通讯']

    # 限制创建通讯时，发起人必须有自己
    inviter = names[0]
    if inviter != info['name']:
        return False, FAIL + "通讯创建失败，自己的名字必须放在第一个名字！格式:通讯·角色名称&角色名称"


    # 创建通讯频道
    payload = {
        'guild_id':info['guild_id'],
        'parent_id':parent_id,
        'name':f"通讯：{content}"
    }
    response = requests.post(url + '/v3/channel/create', headers=bk_header, json=payload)
    msg = json.loads(response.text)
    logger.info(msg)
    created_channel_id = msg['data']['id']

    # 更新频道角色
    for name in names:
        p_channel_id = sData['solos'][name]
        p_role_id = sData['roles'][name]
        updateChannelRole(created_channel_id,p_role_id)

        # 返回成功信息
        reply_content = SUCCESS + f"通讯创建成功：(chn){created_channel_id}(chn)"
        sendMessage(p_channel_id,reply_content,9)

    return True,reply_content

def createEPChannels(message, msg):
    channel_id = msg.target_id
    content = message.replace("创建频道·", "").strip()
    lines = content.split("\n")
    if len(lines) < 2:
        return FAIL + "创建频道失败，格式错误！格式：\n创建频道·EPX\n官约：角色A&角色B\n踩点：角色C&角色D"

    ep_name = lines[0].strip()
    if not ep_name.startswith("EP"):
        return FAIL + "创建频道失败，EP编号格式错误！格式：\n创建频道·EPX\n官约：角色A&角色B\n踩点：角色C&角色D"

    sData = getsDataJsonByChannelId(channel_id)
    if ep_name not in sData['parents'].keys():
        return FAIL + f"创建频道失败，未找到 EP 分类 [{ep_name}]，请先在恋综配置中添加"

    parent_id = sData['parents'][ep_name]
    guild_id = sData['guild_id']
    reply_messages = []

    for line in lines[1:]:
        line = line.strip()
        if not line:
            continue
        channel_type, players = line.split("：", 1)
        players = players.strip().split("&")
        channel_name = line
        roles = []
        for pname in players:
            pname = pname.strip()
            if pname in sData['roles'].keys() and sData['roles'][pname]:
                roles.append(sData['roles'][pname])

        created_channel_id = createChannel(guild_id, parent_id, channel_name, roles)
        reply_messages.append(f"{channel_name} 创建成功：(chn){created_channel_id}(chn)")
        createRecord(sData['sName'],players,players[0],ep_name,created_channel_id,channel_name)

    if reply_messages:
        return "\n".join(reply_messages)
    else:
        return FAIL + "创建频道失败，未解析到有效的频道信息"

def sendMessage(target_id, content,type):
    payload = {
        "target_id": target_id,
        "type": type,
        "content": content
    }

    response = requests.post(url + "/v3/message/create", headers=bk_header, json=payload)
    logger.info(response.text)
    return response

def getChannelMessageList(channel_id):
    params = {
        "target_id": channel_id,
        "page_size": 100
    }
    response = requests.get(url + "/v3/message/list", headers=bk_header, params=params)
    msg = json.loads(response.text)
    return msg['data']['items']


def getLatestMessage(channel_id):
    params = {
        "target_id": channel_id,
        "page_size": 1
    }
    response = requests.get(url + "/v3/message/list", headers=bk_header, params=params)
    msg = json.loads(response.text)
    return msg['data']['items']

def isAdmin(user_id, sData):
    """检查用户是否为当前恋综的管理员"""
    admins = sData.get('admins', [])
    if str(user_id) in admins:
        return True
    return False

def addAdmin(message, msg):
    """添加管理员
    格式：添加管理员·恋综名称 @玩家
    """
    contents = message.replace("添加管理员·", "").strip().split(" ")
    if len(contents) < 2:
        return FAIL + "格式错误：添加管理员·恋综名称 @玩家"

    sName = contents[0]
    user_ids = [c.replace("(met)", "").strip() for c in contents[1:] if c.strip()]

    flag, sData = loadData(sName)
    if not flag:
        return FAIL + f"找不到恋综 [{sName}]"

    if 'admins' not in sData:
        sData['admins'] = []

    added = []
    already = []
    for user_id in user_ids:
        if user_id not in sData['admins']:
            sData['admins'].append(user_id)
            added.append(user_id)
        else:
            already.append(user_id)

    if added:
        setData(sName, sData)
    result = []
    if added:
        result.append(f"已添加：{'、'.join(added)}")
    if already:
        result.append(f"已是管理员：{'、'.join(already)}")
    return SUCCESS + "操作完成\n" + "\n".join(result)

def removeAdmin(message, _msg):
    """移除管理员
    格式：移除管理员·恋综名称 @玩家
    """
    contents = message.replace("移除管理员·", "").strip().split(" ")
    if len(contents) < 2:
        return FAIL + "格式错误：移除管理员·恋综名称 @玩家"

    sName = contents[0]
    user_ids = [c.replace("(met)", "").strip() for c in contents[1:] if c.strip()]

    flag, sData = loadData(sName)
    if not flag:
        return FAIL + f"找不到恋综 [{sName}]"

    if 'admins' not in sData:
        return FAIL + f"[{sName}] 没有管理员"

    removed = []
    not_found = []
    for user_id in user_ids:
        if user_id in sData['admins']:
            sData['admins'].remove(user_id)
            removed.append(user_id)
        else:
            not_found.append(user_id)

    if removed:
        setData(sName, sData)

    result = []
    if removed:
        result.append(f"已移除：{'、'.join(removed)}")
    if not_found:
        result.append(f"非管理员：{'、'.join(not_found)}")

    return SUCCESS + "操作完成\n" + "\n".join(result)

def getStatistics(msg):
    """统计恋综整体情况"""
    channel_id = msg.target_id
    user_id = msg.author_id

    sData = getsDataJsonByChannelId(channel_id)
    if not isAdmin(user_id, sData):
        return FAIL + "仅管理员可使用此功能"

    sName = sData['sName']
    guild_id = sData['guild_id']
    parents = sData.get('parents', {})

    lines = [f"**[{sName}] 数据统计**\n"]

    # 按 EP 分别统计
    ep_stats = {}
    totals = {"私约": 0, "踩点": 0, "心愿": 0}

    for parent_name, parent_id in parents.items():
        if parent_name == '通讯':
            continue
        channels = getChannelListByParentId(guild_id, parent_id)
        ep_stats[parent_name] = { "私约": 0, "踩点": 0, "心愿": 0}

        for ch in channels:
            ch_name = ch.get('name', '')
            if '：' in ch_name:
                category = ch_name.split('：')[0]
                if category in ep_stats[parent_name]:
                    ep_stats[parent_name][category] += 1
                    totals[category] += 1

    # 输出每个 EP 的统计
    for ep_name in sorted(ep_stats.keys()):
        stats = ep_stats[ep_name]
        parts = f"**{ep_name}** : "
        for cat, count in stats.items():
            if count > 0:
                parts += f" {cat}： {count} |"
        if parts.endswith('|'):
            parts = parts[:-1]
        lines.append(parts)

    # 输出汇总
    lines.append("\n**汇总**")
    summary_parts = [f"{k}： {v}" for k, v in totals.items() if v > 0]
    lines.append(" | ".join(summary_parts))
    wechat_channels_items = getChannelListByParentId(sData['guild_id'],sData['parents']['通讯'])
    lines.append(f"通讯：{len(wechat_channels_items)}")

    return "\n".join(lines)

def getsDataJsonByChannelId(channel_id):
    guild_id = getChannelInfo(channel_id)['guild_id']
    sName = loadData("data")[1]['guilds'][guild_id]
    sData = loadData(sName)[1]
    return sData

def inviteMinidate(mesaage,msg):
    logger.info(mesaage)
    channel_id = msg.target_id
    content = mesaage.replace("私约·","").strip()
    if ("发起人：" in content
        and "接收人：" in content):
        # 获取恋综信息
        sData = getsDataJsonByChannelId(channel_id)
        EP = content.split("发起人：")[0].strip()

        if EP not in sData['parents'].keys():
            return False, FAIL +  f"[{sData['sName']}] 缺少 [{EP}] 分组ID，请联系管理员"


        try:

            sender_name = content.split("发起人：", 1)[1].split("接收人：", 1)[0].strip()
            recever_name = content.split("接收人：", 1)[1].split("时间：", 1)[0].strip()

            if sender_name != msg.ctx.channel.name:
                return False,FAIL + "发起人错误，请检查。"
            if sender_name not in sData['solos'].keys() or recever_name not in sData['solos'].keys():
                return False, FAIL + f"发起人/接收人 不存在，请检查。"
            if sender_name == recever_name:
                return False, FAIL + f"发起人和接收人不能相同。"

            recever_channel_id = sData['solos'][recever_name]
            p_content =T.getMiniDateInviteContent(content,msg.author.avatar) #content,EP,icon_src,sender,time,address,note
            response = sendMessage(recever_channel_id,p_content,10)

            return True, SUCCESS + "私约邀请已发送"

        except Exception as e:
            logger.error(e)
            return False,FAIL + f"{T.MINIDATE_CREATE}"
    else:
        return False, FAIL + f"{T.MINIDATE_CREATE}"

def acceptMinidate(mesaage,channel_id,msg_id):
    content = mesaage.replace("接受私约·","").strip()
    if ("发起人：" in content
        and "接收人：" in content):

        # 获取恋综信息
        sData = getsDataJsonByChannelId(channel_id)
        EP = content.split("发起人：")[0].strip()
        parent_id = sData['parents'][EP]
        guild_id = sData['guild_id']

        # 使按钮失效
        flag, r = disEnableButton(content,msg_id=msg_id,m="已接受")
        if flag: r = SUCCESS +  "接受私约成功"

        try:
            sender_name = content.split("发起人：", 1)[1].split("接收人：", 1)[0].strip()
            recever_name = content.split("接收人：", 1)[1].split("时间：", 1)[0].strip()

            recever_channel_id = sData['solos'][recever_name]
            sender_channel_id = sData['solos'][sender_name]

            roles = []
            roles.append(sData['roles'][recever_name])
            roles.append(sData['roles'][sender_name])

            name = f"私约：{sender_name}&{recever_name}"
            created_channel_id = createChannel(guild_id,parent_id,name,roles)

            telling = SUCCESS +  f"私约已创建，一键直达：(chn){created_channel_id}(chn)"

            sendMessage(recever_channel_id,telling,9)
            sendMessage(sender_channel_id,telling,9)

            

            # 增加个人档案记录 - senderName
            createRecord(sData['sName'],[sender_name,recever_name],sender_name,EP,created_channel_id,name)

            return flag, r

        except Exception as e:
            logger.error(e)
            return False,f"{T.MINIDATE_CREATE}"
    else:
        return False, f"{T.MINIDATE_CREATE}"

def createRecord(sName,name_list,sender_name,EP,channel_id,channel_name):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    for pname in name_list:
        pData = readRecord(sName, pname)
        if channel_id in pData['details'].keys(): continue
        pData['groups'] += 1
        channel_info = {
            'is_finished': 0,
            'counts':0,
            'last_time': now,
            'current_person': sender_name,
            'channel_name':channel_name,
            'EP':EP,
            'content': []
        }
        pData["details"][channel_id] = channel_info
        saveRecord(sName, pname, pData)

def readRecord(sName,pName):
    filename = f"./data/{sName}/{pName}.json"
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def saveRecord(sName,pName,data):
    filename = f"./data/{sName}/{pName}.json"
    with open(filename, "w", encoding="utf-8") as w:
        json.dump(data, w, indent=4, ensure_ascii=False)
    return


def createChannel(guild_id, parent_id, name, roles=None):
    payload = {
        'guild_id': guild_id,
        'parent_id': parent_id,
        'name': name
    }
    response = requests.post(url + '/v3/channel/create', headers=bk_header, json=payload)
    msg = json.loads(response.text)
    created_channel_id = msg['data']['id']

    # 更新频道角色
    if roles:
        for role_id in roles:
            updateChannelRole(created_channel_id, role_id)

    return created_channel_id

def rejectMinidate(mesaage,channel_id,msg_id):
    content = mesaage.replace("拒绝私约·","").strip()
    # 获取恋综信息
    sData = getsDataJsonByChannelId(channel_id)
    sender_name = content.split("发起人：", 1)[1].split("接收人：", 1)[0].strip()
    recever_name = content.split("接收人：", 1)[1].split("时间：", 1)[0].strip()
    sender_channel_id = sData['solos'][sender_name]
    msg =FAIL + f"**发向{recever_name}的私约邀请已被拒绝**\n\n"
    sendMessage(sender_channel_id,msg,9)
    flag, r = disEnableButton(content,msg_id,m="已拒绝")
    if flag: r = SUCCESS + "拒绝私约成功"
    return flag, r

def updateMessage(msg_id, content):
    payload = {
        "msg_id": msg_id,
        "content": content
    }
    response = requests.post(url + "/v3/message/update", headers=bk_header, json=payload)
    logger.info(response.text)
    return response

def disEnableButton(content,msg_id,m):
    # 使按钮失效
    disenable_content = T.getMiniDateDisEnableContent(content,m)
    response = updateMessage(msg_id, disenable_content)

    return True, response

def noteTo(message, channel_id):
    try:
        content = message.replace("To","").strip().split(" ",1)
        toName, note = content[0].strip(), content[1].strip()

        sData = getsDataJsonByChannelId(channel_id)

        # 从 solos 中获取与该频道值匹配 value 对应的 key 作为发送者
        sender = None
        for name, ch_id in sData.get('solos', {}).items():
            if ch_id == channel_id:
                sender = name
                break
        if not sender:
            return False,channel_id,FAIL + "当前频道错误，非个人频道，无法获取发送者"

    except Exception as e:
        logger.error(e)
        return False, channel_id, "To角色名称 这里是纸条内容"

    if toName not in sData['solos']:
        return False,channel_id, FAIL + f"[{toName}] 不存在，请检查或联系管理员"

    c = template.getNoteTemplate(note, sender, toName)
    toChannelId = sData['solos'][toName]
    sendMessage(toChannelId,c,10)

    # reply_msg  = f"纸条 From {sender}: \n{note}"
    return True, toChannelId, SUCCESS + "转发成功"

def sendGift(message,msg):

    channel_id = msg.target_id
    imgs = []
    try:
        toName = message.split("礼物·", 1)[1].split("送礼者：", 1)[0].strip()
        parts = parse_kv(message, "送礼者：", "收礼者：", "时间：", "内容：", "留言：")
        sender = parts["送礼者："]
        receiver = parts["收礼者："]
        time = parts["时间："]
        gift = parts["内容："]
        note = parts["留言："]
    except Exception as e:
        logger.error(e)
        return False, FAIL + "格式错误！\n" + template.GIFT

    if gift == "" or note == "":
        return False, FAIL + "内容不得为空" + "\n" + template.GIFT

    sData = getsDataJsonByChannelId(channel_id)
    if toName not in sData['solos']:
        return False, channel_id, f"[{toName}] 不存在，请检查或联系管理员"

    toChannelId = sData['solos'][toName]
    if msg.type == 10:
        contents = json.loads(msg.content)
        modules = contents[0]['modules']
        imgs = []
        count = len(modules)
        for i in range(1,count):
            img_src = modules[i]['elements'][0]['src']
            imgs.append(img_src)

        c = T.getGiftTemplate(sender,receiver,gift,note,time,imgs)
    else:
        c = template.getGiftTemplate(sender,receiver,gift,note,time,imgs=None)

    sendMessage(toChannelId,c,10)
    return True, SUCCESS + "礼物发送成功！"

def systemSendLetters(msg):
    sData = getsDataJsonByChannelId(msg.target_id)
    letter_file = sData['sName'] + "letter"
    letter_path = os.path.join(PATH, letter_file + ".json")

    letter_data = loadData(letter_file)[1]
    cnt = 0
    for key in letter_data.keys():
        letters = letter_data[key]
        if len(letters) == 0: continue
        cnt += len(letters)
        for item in letters:
            c = T.getLetterTemplate(item['sender_name'],item['content'],item['imgs'])
            recever_name = item['recever_name']
            target_id = sData['solos'][recever_name]
            sendMessage(target_id,c,10)

        sendMessage(msg.target_id,f"信 from {key} 已发送, 共{len(letters)}封。",9)
    sendMessage(msg.target_id, SUCCESS + f"发送完毕， 共{cnt}封。",9)

    if cnt == 0:
        return

    # 备份 letter.json
    if os.path.exists(letter_path):
        backup_dir = os.path.join(PATH, sData['sName'])
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"letter_backup_{timestamp}.json")
        shutil.copy2(letter_path, backup_path)

    # 清空 letter.json
    empty_data = {k: [] for k in letter_data.keys()}
    setData(letter_file, empty_data)



def getImgSrcsFromCardMessage(msg):
    contents = json.loads(msg.content)
    modules = contents[0]['modules']
    imgs = []
    count = len(modules)
    for i in range(1,count):
        img_src = modules[i]['elements'][0]['src']
        imgs.append(img_src)
    return imgs
def publicWish(message,channel_id):

    try:
        EP = message.split("心愿·", 1)[1].split("署名：", 1)[0].strip()
        parts = parse_kv(message, "署名：", "内容：", "时间：")
        sender_name = parts["署名："]
        wish = parts["内容："]
        time = parts["时间："]
    except Exception as e:
        logger.error(e)
        return FAIL + f"格式错误！\n {template.CREATE_WASH}"


    info = getChannelInfo(channel_id)
    publish_name = info['name']
    guild_name = info['guild_name']


    publish_content = template.getWashWallContent(message,EP,sender_name,wish,time,publish_name,0)
    # publish_content = template.getWashWallContent(message,EP,publish_name,wish,time,sender_name,0)
    sData = loadData(guild_name)[1]
    wash_channel_id = sData['public_channels'][template.KEY_WISHWALL]

    if EP != sData['current_EP'] or wish == '' or time == '':
        return FAIL + f"格式错误！\n {template.CREATE_WASH}"

    sendMessage(wash_channel_id,publish_content,10)
    return SUCCESS + "心愿发布成功！"
    # sendMessage()

def goWish(message,channel_id,recever_name,msg_id):
    content = message

    # 获取恋综信息
    sData = getsDataJsonByChannelId(channel_id)
    EP = message.split("心愿·", 1)[1].split("署名：", 1)[0].strip()
    parts = parse_kv(message, "署名：", "内容：", "时间：", "发布人：")
    publish_name = parts["署名："]
    wish = parts["内容："]
    time = parts["时间："]
    sender_name = parts["发布人："]

    parent_id = sData['parents'][EP]
    guild_id = sData['guild_id']

    recever_channel_id = sData['solos'][recever_name]
    sender_channel_id = sData['solos'][sender_name]

    if recever_name == sender_name:
        sendMessage(sender_channel_id,FAIL + "操作失败，发布心愿者不能领取",9)
        return False, FAIL + "操作失败，发布心愿者不能领取"

    roles = []
    roles.append(sData['roles'][recever_name])
    roles.append(sData['roles'][sender_name])

    name = f"心愿：{recever_name}&{sender_name}"
    created_channel_id = createChannel(guild_id, parent_id, name, roles)

    telling = SUCCESS + f"心愿已发起：(chn){created_channel_id}(chn)"

    sendMessage(recever_channel_id, telling, 9)
    sendMessage(sender_channel_id, telling, 9)

    disEnableWishContent = template.getWashWallContent(message,EP,publish_name,wish,time,publish_name,1)
    updateMessage(msg_id,disEnableWishContent)

    # 增加个人档案记录 - senderName
    createRecord(sData['sName'], [sender_name, recever_name], recever_name, EP, created_channel_id,name)

    return True, "success"

def sendCaidian(message, msg):
    channel_id = msg.target_id
    content = message.replace("踩点·", "").strip()
    locations = [loc.strip() for loc in content.split("、") if loc.strip()]
    if len(locations) == 0:
        return FAIL + "踩点失败，格式错误！格式：踩点·A、B、C、D、E、F"
    
    sData = getsDataJsonByChannelId(channel_id)
    if 'caidian' not in sData:
        sData['caidian'] = {}
    sData['caidian']['locations'] = locations
    sData['caidian']['selections'] = {}
    setData(sData['sName'], sData)

    card_content = template.getCaidianContent(locations)
    sendMessage(sData['public_channels'][template.KEY_CAIDIAN], card_content, 10)
    return SUCCESS + f"踩点卡片已发送，共 {len(locations)} 个地点"

def selectCaidian(message, user_nickname, channel_id):
    user_nickname = user_nickname.strip()
    location = message.replace("踩点选择·", "").strip()
    sData = getsDataJsonByChannelId(channel_id)
    rpl = ""
    
    if location not in sData['caidian']['locations']:
        rpl = FAIL + f"选择失败，[{location}] 不存在"

    if user_nickname not in sData['solos'].keys():
        rpl = FAIL + f"踩点选择失败，[{user_nickname}] 不存在"
        logger.error(rpl)
        return rpl

    sData['caidian']['selections'][user_nickname] = location
    setData(sData['sName'], sData)

    rpl = SUCCESS + f"[{user_nickname}] 已选择：【{location}】"
    solo_id = sData['solos'][user_nickname]
    sendMessage(solo_id,rpl,9)
    return rpl

def getCaidianInfo(channel_id):
    sData = getsDataJsonByChannelId(channel_id)

    if 'caidian' not in sData or 'locations' not in sData['caidian']:
        return FAIL + "暂无踩点信息"

    locations = sData['caidian']['locations']
    selections = sData['caidian'].get('selections', {})

    result = ["**可踩点地点：**"]
    for loc in locations:
        players = [name for name, choice in selections.items() if choice == loc]
        if players:
            result.append(f"- {loc}：{'、'.join(players)}")
        else:
            result.append(f"- {loc}：（暂无）")

    return "\n".join(result)

async def handleFingerGame(message, msg):
    """统一处理折手指系列指令"""
    content = message.replace("折手指·", "").strip()

    if content.startswith("新建"):
        return createFingerGame(content,msg.target_id)

    elif content == "查看":
        return viewFingerGame(msg.target_id)

    elif content == "查看本轮":
        return viewCurrentRound(msg.target_id)

    elif content == "结束":
        return await endFingerGame(msg.target_id, msg)

    else:
        parts = content.split("·")
        if len(parts) < 2:
            return FAIL + "格式错误，折手指指令格式：\n折手指·新建\n折手指·角色名·出题·经历描述\n折手指·角色名·折/不折·题号"

        player_name = parts[0].strip()
        action = parts[1].strip()
        param = parts[2].strip() if len(parts) > 2 else ""

        if action == "出题":
            return askFingerQuestion(player_name, param, msg.target_id)
        elif action in ("折", "不折"):
            round_num = param if param else ""
            return answerFingerQuestion(player_name, action, round_num, msg.target_id)

        return FAIL + "未知操作，支持：出题、折、不折"

def createFingerGame(message,channel_id):
    """创建折手指游戏，从 solos 获取玩家"""
    sData = getsDataJsonByChannelId(channel_id)
    InitFingerCounts = message.replace("新建", "").strip()
    if InitFingerCounts.isdigit():
        InitFingerCounts = int(InitFingerCounts)
    else:
        InitFingerCounts = 12
    players = list(sData.get('solos', {}).keys())

    if len(players) < 2:
        return FAIL + "游戏需要至少2名玩家，请先绑定角色"

    
    game_file = f"./data/finger_game/{channel_id}.json"
    if os.path.exists(game_file):
        return FAIL + "当前游戏尚未结束，请先结束游戏"
    os.makedirs("./data/finger_game", exist_ok=True)
    game_data = {
        "sName": sData['sName'],
        "game_id": channel_id,
        "players": players,
        "fingers": {p: InitFingerCounts for p in players},
        "status": {p: "active" for p in players},
        "current_round": 0,
        "questions": {},
        "all_folded_count": 0
    }

    with open(game_file, 'w', encoding='utf-8') as f:
        json.dump(game_data, f, indent=4, ensure_ascii=False)
    
    return SUCCESS + f"折手指游戏创建成功！\n玩家：{'、'.join(players)}\n初始手指数：{InitFingerCounts}根"

def getFingerGameData(channel_id):
    """获取当前游戏数据"""
    game_file = f"./data/finger_game/{channel_id}.json"
    if not os.path.exists(game_file):
        return None, None
    with open(game_file, 'r', encoding='utf-8') as f:
        game_data = json.load(f)
    return game_data, game_file

def saveFingerGameData(game_data, game_file):
    """保存游戏数据"""
    with open(game_file, 'w', encoding='utf-8') as f:
        json.dump(game_data, f, indent=4, ensure_ascii=False)

def askFingerQuestion(player_name, question, channel_id):
    """出题"""
    game_data, game_file = getFingerGameData(channel_id)
    if not game_data:
        return FAIL + "暂无进行中的游戏，请先创建：折手指·新建"

    if player_name not in game_data['players']:
        return FAIL + f"玩家 [{player_name}] 不在游戏中，请检查角色名"

    game_data['current_round'] += 1
    round_num = str(game_data['current_round'])
    game_data['questions'][round_num] = {
        "text": question,
        "asker": player_name,
        "answers": {}
    }
    saveFingerGameData(game_data, game_file)

    lines = [f"**【折手指 · 第{round_num}题】**\n"]
    lines.append(f"**{player_name}** ：")
    lines.append(f"{question}\n")
    lines.append(f"\n请其他玩家回复：折手指·姓名·折/不折·题{round_num}")

    return "\n".join(lines)

def answerFingerQuestion(player_name, answer, round_num, channel_id):
    """回答问题"""
    game_data, game_file = getFingerGameData(channel_id)
    if not game_data:
        return FAIL + "暂无进行中的游戏"

    if player_name not in game_data['players']:
        return FAIL + f"玩家 [{player_name}] 不在游戏中"

    if game_data['status'][player_name] == "out":
        return FAIL + f"玩家 [{player_name}] 已出局"

    if not round_num:
        round_num = str(game_data['current_round'])
    else:
        round_num = round_num.replace("题", "")

    if round_num not in game_data['questions']:
        return FAIL + f"第{round_num}题不存在"

    question_data = game_data['questions'][round_num]

    if player_name in question_data['answers']:
        old_answer = question_data['answers'][player_name]
        return FAIL + f"你已在第{round_num}题回答过 [{old_answer}]，无法重复回答"

    if player_name == question_data['asker']:
        return FAIL + "自己出的题不需要回答"

    question_data['answers'][player_name] = answer

    result_msg = ""
    if answer == "折":
        game_data['fingers'][player_name] -= 1
        if game_data['fingers'][player_name] <= 0:
            game_data['status'][player_name] = "out"
            result_msg = f"💀 [{player_name}] 回答 **折**，手指已折完，**出局**！"
        else:
            result_msg = f"✅ [{player_name}] 回答 **折**，剩余 {game_data['fingers'][player_name]} 根手指"
    else:
        result_msg = f"✅ [{player_name}] 回答 **不折**，保留 {game_data['fingers'][player_name]} 根手指"

    active_after = [p for p in game_data['players'] if game_data['status'][p] != "out"]
    if len(active_after) == 1:
        saveFingerGameData(game_data, game_file)
        return SUCCESS + f"{result_msg}\n\n🏆 游戏结束！获胜者：**{active_after[0]}**"

    all_players = set(game_data['players']) - {question_data['asker']}
    active_players = set(p for p in all_players if game_data['status'][p] != "out")
    answered = set(question_data['answers'].keys()) - {question_data['asker']}
    unanswered = active_players - answered

    if unanswered:
        saveFingerGameData(game_data, game_file)
        return SUCCESS + result_msg
    else:
        all_folded = all(question_data['answers'].get(p) == "折" for p in active_players)
        if all_folded and len(active_players) > 1:
            asker = question_data['asker']
            game_data['fingers'][asker] -= 1
            if game_data['fingers'][asker] <= 0:
                game_data['status'][asker] = "out"
            saveFingerGameData(game_data, game_file)
            extra_msg = f"\n⚠️ 所有玩家都回答折，{asker} 额外折一根！"
            if game_data['status'][asker] == "out":
                extra_msg += f"\n💀 [{asker}] 出局！"
            return SUCCESS + result_msg + extra_msg
        else:
            saveFingerGameData(game_data, game_file)
            return SUCCESS + result_msg

def viewFingerGame(channel_id):
    """查看所有人手指数"""
    game_data, _ = getFingerGameData(channel_id)
    if not game_data:
        return FAIL + "暂无进行中的游戏"

    lines = ["**【折手指游戏】当前状态：**\n"]

    for p in game_data['players']:
        fingers = game_data['fingers'][p]
        lines.append(f"- {p}：{fingers}根")

    lines.append(f"\n当前进行到第{game_data['current_round']}轮")

    return "\n".join(lines)

def viewCurrentRound(channel_id):
    """查看当前轮答题情况"""
    game_data, _ = getFingerGameData(channel_id)
    if not game_data:
        return FAIL + "暂无进行中的游戏"

    round_num = str(game_data['current_round'])
    if round_num not in game_data['questions']:
        return FAIL + "暂无进行中的题目"

    question_data = game_data['questions'][round_num]
    lines = [f"**【第{round_num}题】**\n"]
    lines.append(f"题目：{question_data['text']}")
    lines.append(f"出题人：{question_data['asker']}\n")

    answers = question_data['answers']
    all_players = set(game_data['players']) - {question_data['asker']}
    active_players = set(p for p in all_players if game_data['status'][p] != "out")

    answered = set(answers.keys()) - {question_data['asker']}
    unanswered = active_players - answered

    folded = [p for p in answered if answers.get(p) == "折"]
    not_folded = [p for p in answered if answers.get(p) == "不折"]

    if folded:
        lines.append(f"折：{'、'.join(folded)}")
    if not_folded:
        lines.append(f"不折：{'、'.join(not_folded)}")
    if unanswered:
        lines.append(f"待回答：{'、'.join(unanswered)}")

    return "\n".join(lines)

async def endFingerGame(channel_id, msg):
    """结束折手指游戏，上传数据文件后删除"""
    game_data, game_file = getFingerGameData(channel_id)
    if not game_data:
        return FAIL + "暂无进行中的游戏"

    if not os.path.exists(game_file):
        return FAIL + "游戏文件不存在"

    try:
        file_url = await bot.client.create_asset(game_file)
        cm = CardMessage(Card(
            Module.Header("折手指游戏记录"),
            Module.File(type="file", src=file_url, title=f"折手指_{channel_id}.json")
        ))
        await msg.reply(cm)
    except Exception as e:
        logger.error(e)
        await msg.reply(FAIL + "文件上传失败")

    # 删除本地文件
    try:
        os.remove(game_file)
    except Exception:
        pass

    return SUCCESS + "游戏已结束，数据已归档"

def updateSData(message):
    try:
        contents = message.replace("更改信息·","").strip().split(" ")
        sName = contents[0]
        p = contents[1]
        key = contents[2]
        value = contents[3]

        sData = loadData(sName)[1]
        sData[p][key] = value

    except Exception as e:
        return FAIL + "操作失败，更改格式：更改信息·恋综名称 parents key value"

    flag, msg = setData(sName, sData)
    if flag: msg = SUCCESS + f"[{sName}] 信息更改成功！"
    return msg

def publicNote(message,msg):
    try:
        sender = message.split("FROM：",1)[1].split("时间：",1)[0].strip()
        time = message.split("时间：",1)[1].split("内容：",1)[0].strip()
        content = message.split("内容：",1)[1].strip()

        if content == "":
            return False, FAIL + "内容不得为空"

        c = template.getPublicNoteTemplate(content,sender,time)
        info = getsDataJsonByChannelId(msg.target_id)

        public_note_channel_id = info['public_channels'][template.KEY_PUBLIC_NOTE]
        sendMessage(public_note_channel_id,c,10)
        return True,SUCCESS + "发送成功！"


    except Exception as e:
        logger.error(e)
        return False, template.PUBLIC_NOTE


if __name__ == '__main__':
    print("bot run")
    bot.run()