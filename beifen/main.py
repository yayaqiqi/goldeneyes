from khl import Bot, Message, MessageTypes, Event, EventTypes
from khl.card import Card, CardMessage, Module, Types, Element, Struct
import json
import logging
import datetime
import os
import requests

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

config = loadData('config')[1]
bot = Bot(token=config['token'])
bk_header = {f'Authorization': f"Bot {config['token']}", f"Content-Type": f"application/json"}
url ="https://www.kookapp.cn/api"

@bot.on_message()
async def handle_all_messages(msg: Message):

    print(msg.__dict__) # todo deleted

    if msg._channel_type != 'GROUP': return

    message = getMsgContent(msg).strip()
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
        flag, rpl = inviteMinidate(message,msg.target_id)
        await msg.reply(rpl)

    elif message.startswith("纸条·"):
        flag, target_id, rpl = noteTo(message,msg.target_id)
        target_ch = await bot.client.fetch_public_channel(target_id)
        await target_ch.send(rpl)
        if flag: await msg.reply("纸条已传递")

    elif message.startswith("礼物·"):
        has_img = 0
        if msg.type == 10: has_img = 1
        flag,target_id,rpl = sendGift(message,has_img,msg.target_id)
        if flag:
            target_ch = await bot.client.fetch_public_channel(target_id)
            await target_ch.send(rpl)
            await msg.reply("礼物已传递")
        else:
            await msg.reply(rpl)

    elif message.startswith("点歌台"):
        guild_id  = getChannelInfo(msg.target_id)['guild_id']
        name = loadData('data')[1]['guilds'][guild_id]
        info  = loadData(name)[1]
        music_channel_id = info['public_channels'][template.KEY_MUSIC]
        target_ch = await bot.client.fetch_public_channel(music_channel_id)
        await target_ch.send(message)

    elif message.startswith("公共留言"):
        guild_id = getChannelInfo(msg.target_id)['guild_id']
        name = loadData('data')[1]['guilds'][guild_id]
        info = loadData(name)[1]
        music_channel_id = info['public_channels'][template.KEY_PUBLIC_NOTE]
        target_ch = await bot.client.fetch_public_channel(music_channel_id)
        await target_ch.send(message)

    elif message.startswith("心愿·"):
        publicWish(message,msg.target_id)

    elif message.startswith("心动信"):
        rpl = sendLetters(message,msg.target_id)
        await msg.reply(rpl)


    elif message == "test123":
        print(msg.ctx.guild.id)
        print(msg.ctx.channel.id)
        ch = msg.ctx.channel
        print(ch.__dict__)
    elif message == "回戏档案":
        reply_msg = myPlayCheck(msg.target_id)
        await msg.reply(reply_msg)

    elif message == "结束对戏":
        endPlay(msg)
        pass

    else:
        first_line = message.split("\n",1)[0].strip()
        info = getChannelInfo(msg.target_id)
        sData = loadData(info['guild_name'])[1]
        names = sData['solos'].keys()
        if first_line in names:
            playedUpdatedRecord(message,msg)

@bot.on_message()
async def record_play(msg: Message):
    # 排除机器人自身消息和指令消息
    message = msg.content.strip()


@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)
async def handle_all_events(msg:Message, e:Event):

    print(e.__dict__)
    message = e.extra['body']['value']
    msg_id = e.extra['body']['msg_id']
    target_id = e.extra['body']['target_id']
    user_nickname = e.extra['body']['user_info']['nickname']

    ch = await bot.client.fetch_public_channel(target_id) # 获取频道

    if message.startswith("接受私约·"):
        flag,rpl = acceptMinidate(message,target_id)
        if not flag:
              # 获取频道
            await ch.send(rpl, quote=msg_id)
            await ch.send("接受私约操作失败，请联系管理员", quote=msg_id)


    elif message.startswith("拒绝私约·"):
        flag,rpl = rejectMinidate(message,target_id)
        await ch.send("已拒绝", quote=msg_id)

    elif message.startswith("心愿·"):
        flag, rpl = goWish(message, channel_id=target_id,recever_name=user_nickname,msg_id=msg_id)

def sendLetters(message,channel_id):
    filename = "./data/letter.json"
    letter_file = "letter"

    content = message.replace("心动信", "").strip()
    sData = getsDataJsonByChannelId(channel_id)

    if ("收信人：" in content
            and "发送人：" in content
            and "内容：" in content):
        try:
            recever_name = content.split("收信人：", 1)[1].split("发送人：", 1)[0].strip()
            sender_name = content.split("发送人：", 1)[1].split("内容：", 1)[0].strip()
            msg = content.split("内容：", 1)[1].strip()

            names = sData['solos'].keys()
            if recever_name not in names:
                msg = "收信人错误，请检查格式后重新输入！"
                return msg

            letter_data = loadData("letter")[1]

            with open(filename, "w", encoding="utf-8") as f:
                l = len(letter_data)
                letter_data[l + 1] = content
                json.dump(letter_data, f, indent=4, ensure_ascii=False)

            msg = "已收录。"
            return msg

        except Exception:
            msg = "格式错误，请按照以下格式发送心动信\n" + template.LETTER


    else:
        "格式错误，请按照以下格式发送心动信\n" + template.LETTER

    return msg

def myPlayCheck(channel_id):
    info = getChannelInfo(channel_id)
    sName = info['guild_name']
    pName = info['name']

    pData = readRecord(sName, pName)

    wait_you = "当前等待你回戏的频道：\n"
    wait_others = "当前等待他人回戏的频道：\n"
    details = pData['details']

    for key in details.keys():
        value = details[key]
        if value['is_finished'] == 1: continue
        time = utils.calculate_now_hour_diff(value['last_time'])
        if time <= 24:
            logo = "🟢  "
        elif time <= 48:
            logo = "🟡 "
        else:
            logo = "🔴 "
        line = f"{logo} {value['channel_name']}: (chn){key}(chn) ({time}h)\n"
        if value['current_person'] == pName:
            wait_you = wait_you + line
        else:
            wait_others = wait_others + line

    reply = wait_you + wait_others + "\n" + f"当前共结戏 {pData['finished']} 个。"
    return reply

def endPlay(msg):
    info = getChannelInfo(msg.target_id)
    c_name = msg.ctx.channel.name.strip()
    names = c_name[3:].split("&")
    sName = info['guild_name']
    reply_msg = "————END————"
    for name in names:
        pdata = readRecord(sName,name)
        flag = pdata['details'][msg.target_id]['is_finished']
        if flag == 1: reply_msg = FAIL + "请勿重复操作"
        else:
            pdata['details'][msg.target_id]['is_finished'] = 1
            pdata['finished'] += 1
            saveRecord(sName,name,pdata)

    sendMessage(msg.target_id,reply_msg,9)
    return

def playedUpdatedRecord(message, msg):
    first_line = message.split("\n", 1)[0].strip()
    info = getChannelInfo(msg.target_id)
    sData = loadData(info['guild_name'])[1]
    names = sData['solos'].keys()
    channel_name = info['name'].strip()
    persons = channel_name[3:].split("&")

    # 更新个人档案
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    for i in range(len(persons)):
        if first_line == persons[i]:
            current_person = persons[(i + 1) % len(persons)]
            break;

    for pname in persons:
        pdata = readRecord(sData['sName'], pname)
        pdata['details'][msg.target_id]['last_time'] = now
        pdata['details'][msg.target_id]['current_person'] = current_person
        pdata['details'][msg.target_id]['content'].append(message)
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
    print(contents)
    try:
        sName, pName,user_id,role_id = contents[0], contents[1],contents[2], contents[3]
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
    for key, value in sData['solos'].items():
        if value == group_id:
            remove_name = key
            sData['solos'].pop(key)
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
    created_channel_id = msg['data']['id']

    # 更新频道角色
    for name in names:
        p_channel_id = sData['solos'][name]
        p_role_id = sData['roles'][name]
        updateChannelRole(created_channel_id,p_role_id)

        # 返回成功信息
        reply_content = SUCCESS + f"通讯创建成功：(chn){created_channel_id}(chn)"
        sendMessage(p_channel_id,reply_content,9)

    return True

def sendMessage(target_id, content,type):
    payload = {
        "target_id": target_id,
        "type": type,
        "content": content
    }

    response = requests.post(url + "/v3/message/create", headers=bk_header, json=payload)
    logger.info(response.text)
    return response

def getsDataJsonByChannelId(channel_id):
    guild_id = getChannelInfo(channel_id)['guild_id']
    sName = loadData("data")[1]['guilds'][guild_id]
    sData = loadData(sName)[1]
    return sData

def inviteMinidate(mesaage,channel_id):
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
            # return True,f"{sender_name},{recever_name}"

            if sender_name not in sData['solos'].keys() or recever_name not in sData['solos'].keys():
                return False, FAIL + f"发起人/接收人 不存在，请检查。"

            recever_channel_id = sData['solos'][recever_name]
            p_content =T.getMiniDateInviteContet(content)
            response = sendMessage(recever_channel_id,p_content,10)

            msg = json.loads(response.text)
            msg_id = msg['data']['msg_id']
            #  更新按钮信息 msg_id
            new_content = T.getMiniDateInviteContet(content,1,msg_id)
            u_response = updateMessage(msg_id,new_content)

            return True, SUCCESS + "邀请已发送 "

        except Exception as e:
            logger.error(e)
            return False,FAIL + f"{T.MINIDATE_CREATE}"
    else:
        return False, FAIL + f"{T.MINIDATE_CREATE}"

def acceptMinidate(mesaage,channel_id):
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
            flag, r = disEnableButton(content)
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
        pData['groups'] += 1
        channel_info = {
            'is_finished': 0,
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

def rejectMinidate(mesaage,channel_id):
    content = mesaage.replace("拒绝私约·","").strip()
    # 获取恋综信息
    sData = getsDataJsonByChannelId(channel_id)
    sender_name = content.split("发起人：", 1)[1].split("接收人：", 1)[0].strip()
    sender_channel_id = sData['solos'][sender_name]
    msg = "**私约邀请已被拒绝**\n\n" + content
    sendMessage(sender_channel_id,msg,9)
    flag, r = disEnableButton(content)
    if flag: r = "拒绝私约成功"
    return flag, r

def updateMessage(msg_id, content):
    payload = {
        "msg_id": msg_id,
        "content": content
    }
    response = requests.post(url + "/v3/message/update", headers=bk_header, json=payload)
    logger.info(response.text)
    return response

def disEnableButton(content):
    # 使按钮失效
    try:
        msg_id = content.split("msg_id：")[1].strip()
    except Exception as e:
        return False,"缺少msg_id，请稍等五秒钟后再操作，或联系管理员"

    content = content.replace(msg_id,"").strip()
    content = content.replace("msg_id：","").strip()
    disenable_content = T.getMiniDateDisEnableContet(content)
    response = updateMessage(msg_id, disenable_content)

    return True, response

def noteTo(message, channel_id):
    try:
        content = message.replace("纸条·","").strip().split("\n",1)
        toName, note = content[0].strip(), content[1].strip()
        sender = getChannelInfo(channel_id)['name']

        sData = getsDataJsonByChannelId(channel_id)
    except Exception as e:
        logger.error(e)
        return False, channel_id, "纸条·角色名称\n这里是纸条内容"

    if toName not in sData['solos']:
        return False,channel_id, f"[{toName}] 不存在，请检查或联系管理员"

    toChannelId = sData['solos'][toName]
    reply_msg  = f"纸条 From {sender}: \n{note}"
    return True, toChannelId, reply_msg

def sendGift(message,has_img,channel_id):
    contents = message.replace("礼物·", "").strip().split('\n',1)
    toName,content = contents[0].strip(),contents[1].strip()
    sData = getsDataJsonByChannelId(channel_id)

    if toName not in sData['solos']:
        return False,channel_id, f"[{toName}] 不存在，请检查或联系管理员"

    toChannelId = sData['solos'][toName]
    reply_msg = content
    return True, toChannelId, reply_msg

    if has_img:
        pass
    else:
        pass

def resolvePublicInfo(message,channel_id):
    return message, channel_id

def publicWish(message,channel_id):
    info = getChannelInfo(channel_id)
    publish_name = info['name']
    guild_name = info['guild_name']
    publish_content = template.getWashWallContet(message,publish_name)
    wash_channel_id = loadData(guild_name)[1]['public_channels'][template.KEY_WISHWALL]
    sendMessage(wash_channel_id,publish_content,10)
    # sendMessage()

def goWish(mesaage,channel_id,recever_name,msg_id):

    content = mesaage.replace("心愿·", "").strip()

    # 获取恋综信息
    sData = getsDataJsonByChannelId(channel_id)
    EP = content.split("时间：")[0].strip()
    parent_id = sData['parents'][EP]
    guild_id = sData['guild_id']

    try:
        sender_name = content.split("发布人：", 1)[1].strip()

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

        # 使按钮失效
        idx = mesaage.find("发布人")
        disEnableContent = mesaage[:idx]
        disEnableWishContent = template.getWashWallDisEnableContent(disEnableContent)
        updateMessage(msg_id,disEnableWishContent)

        # 增加个人档案记录 - senderName
        createRecord(sData['sName'], [sender_name, recever_name], recever_name, EP, created_channel_id,name)

        return True, "success"

    except Exception as e:
        logger.error(e)
        print(e)
        return False, f"{T.MINIDATE_CREATE}"

def updateSData(message):
    try:
        contents = message.replace("更改信息·","").strip().split(" ")
        print(contents)
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