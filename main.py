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

    elif message.startswith("通讯·"):
        contents = message.replace("通讯·","").strip()
        flag,rpl = createChat(contents,msg.target_id)
        if not flag: await msg.reply(rpl)

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


    elif message.startswith("心动信"):
        rpl = sendLetters(message,msg)
        await msg.reply(rpl)

    elif message=="撤回心动信":
        rpl = withdrawLetters(msg)
        await msg.reply(rpl)

    elif message == "发送心动信123":
        systemSendGift(msg)

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

    elif message == "结束对戏":
        endPlay(msg)


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
            Module.File(type="file", src=file_url, title='戏录文件')
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
    print(message)
    print(sender)
    print(msg.target_id)
    if ("收信人：" in message
            and "发信人：" in message
            and "内容：" in message):
        # try:
        parts = parse_kv(message, "发信人：", "收信人：", "内容：")
        sender_name = parts["发信人："]
        recever_name = parts["收信人："]
        content = parts["内容："]

        names = sData['solos'].keys()
        print(names)
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
    info = getChannelInfo(channel_id)
    sName = info['guild_name']
    pName = info['name']

    pData = readRecord(sName, pName)

    wait_you = "当前等待你回戏的频道：\n"
    wait_others = "当前等待他人回戏的频道：\n"
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
    rpl = ""
    for name in names:
        precord = readRecord(sName,name)
        channels = precord['details'].keys()
        for channel_id in channels:
            info = precord['details'][channel_id]
            time = info['last_time']
            diff = utils.calculate_now_hour_diff(time)
            if diff > 72 and info['is_finished']==0:
                rpl += channel_id + "\n"
                endPlay(channel_id)
        # saveRecord(sName,name,precord)
    return SUCCESS

def remind(sName):
    sData = loadData(sName)[1]
    names = sData['solos']
    for name in names:
        precord = readRecord(sName,name)
        channels = precord['details'].keys()
        for channel_id in channels:
            info = precord['details'][channel_id]
            time = info['last_time']
            diff = utils.calculate_now_hour_diff(time)
            if diff > 24 and name==info['current_person'] and info['is_finished']==0:
                sendMessage(channel_id,f"(met){sData['user_ids'][name]}(met)",9)
        # saveRecord(sName,name,precord)
    return SUCCESS

def endPlay(channel_id):
    info = getChannelInfo(channel_id)
    c_name = info['name']
    names = c_name[3:].split("&")
    sName = info['guild_name']
    reply_msg = SUCCESS + "记录已更新\n ———— **END** ————"
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

    # try:
    info = getChannelInfoNotRegisted(msg.target_id)
    guild_id = info['guild_id']

    with open(full_file_path, 'w', encoding='utf-8') as f:
        data = {
            "sName": name.strip(),
            "guild_id": guild_id,
            "solos":{},
            "roles":{},
            "parents":{},
            "user_ids":{}
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

    # except Exception as e:
    #     print(e)
    #     return False,f"操作失败:{e}"

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
        info = getChannelInfo(channel_id)
        guild_id = info['guild_id']

        flag, data = loadData("data")
        if not flag: return flag, data
        if guild_id in data['guilds'].keys():
            data['guilds'].pop(guild_id)

        setData('data',data)
        return True,SUCCESS + f"恋综 [{name}] 已清空"


    except Exception as e:
        return False,FAIL + f"操作失败:{e}"

def bindSolo(message,group_id):
    contents = message.replace("绑定·", "").strip().split(" ")
    logger.info(contents)
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

            # 使按钮失效
            flag, r = disEnableButton(content,msg_id=msg_id,m="已接受")
            if flag: r = SUCCESS +  "接受私约成功"

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
        sender = getChannelInfo(channel_id)['name']

        sData = getsDataJsonByChannelId(channel_id)

    except Exception as e:
        logger.error(e)
        return False, channel_id, "To角色名称 这里是纸条内容"

    if toName not in sData['solos']:
        return False,channel_id, f"[{toName}] 不存在，请检查或联系管理员"

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

def systemSendGift(msg):
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

        sendMessage(msg.target_id,f"信 from {key} 已发送",9)
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

    name = f"心愿：{sender_name}&{recever_name}"
    created_channel_id = createChannel(guild_id, parent_id, name, roles)

    telling = f"心愿已发起：(chn){created_channel_id}(chn)"

    sendMessage(recever_channel_id, telling, 9)
    sendMessage(sender_channel_id, telling, 9)


    # disEnableWishContent = template.getWashWallDisEnableContent(disEnableContent)
    disEnableWishContent = template.getWashWallContent(message,EP,name,wish,time,sender_name,1)
    updateMessage(msg_id,disEnableWishContent)

    # 增加个人档案记录 - senderName
    createRecord(sData['sName'], [sender_name, recever_name], recever_name, EP, created_channel_id,name)

    return True, "success"

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

    # elif msg.type == 10:
    #     await msg.reply("10")
    #
    #     contents = json.loads(msg.content)
    #     modules = contents[0]['modules']
    #     # print(contents)
    #     for m in modules:
    #         print(m)
    #
    #         img_src = m['elements'][0]['src']
    #         print(img_src)
    #         cm_json = T.getImgTemplate(img_src)
    #         await  msg.reply(cm_json,type=MessageTypes.CARD)
    # # else: