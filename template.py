import json

KEY_PUBLIC_NOTE = "public_notes"
KEY_MUSIC = "music"
KEY_WISHWALL = "wishwall"

MINIDATE_CREATE ="""私约·EPX
发起人：
接收人：
时间：
地点：
留言："""

GIFT = """礼物·送礼对象
送礼者：可匿名
收礼者：可代号
时间：
内容：
留言："""

ORDER_MUSIC = """点歌台
点歌人： 
收听者： 
时间： 
留言：
歌曲："""

CTEATE_WASH = """心愿·EPX
署名：
内容：
时间： """

PUBLIC_NOTE = """公共留言
FROM： 
时间：
内容："""

LETTER = """心动信
发信人：
收信人：
内容：
"""

def getMiniDateInviteContet_OLD(content, type = 0, msg_id = ""):

    accept_value = "接受私约·" + content
    reject_value = "拒绝私约·" + content
    if type != 0:
        accept_value = accept_value + "\nmsg_id：" + msg_id
        reject_value = reject_value + "\nmsg_id：" + msg_id

    j = [{
        "type": "card",
        "theme": "primary",
        "size": "sm",
        "modules": [
            {
                "type": "section",
                "text": {
                    "type": "plain-text",
                    "content": content
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "action-group",
                "elements": [
                    {
                        "type": "button",
                        "theme": "primary",
                        "value": accept_value,
                        "click": "return-val",
                        "text": {
                            "type": "plain-text",
                            "content": "接受"
                        }
                    },
                    {
                        "type": "button",
                        "theme": "danger",
                        "value": reject_value,
                        "click": "return-val",
                        "text": {
                            "type": "plain-text",
                            "content": "拒绝"
                        }
                    }
                ]
            }
        ]
    }]

    j = json.dumps(j,ensure_ascii=False, indent=4)
    return j

def getMiniDateInviteContent(content,icon_src):


    EP = content.split("发起人：")[0].strip()
    sender = content.split("发起人：", 1)[1].split("接收人：", 1)[0].strip()
    recever_name = content.split("接收人：", 1)[1].split("时间：", 1)[0].strip()
    time = content.split("时间：", 1)[1].split("地点：", 1)[0].strip()
    address = content.split("地点：", 1)[1].split("留言：", 1)[0].strip()
    note = content.split("留言：", 1)[1].strip()

    content = content + "\nicon：" + icon_src
    accept_value = "接受私约·" + content
    reject_value = "拒绝私约·" + content

    j = [{
        "type": "card",
        "size": "sm",
        "theme": "info",
        "modules": [
          {
            "type": "header",
            "text": {
              "type": "plain-text",
              "content": "私约邀请·" + EP
            }
          },
          {
            "type": "divider"
          },
          {
            "type": "section",
            "text": {
              "type": "kmarkdown",
              "content": "**邀请人**"
            }
          },
          {
            "type": "section",
            "mode": "left",
            "accessory": {
              "type": "image",
              "src": icon_src,
              "circle": True
            },
            "text": {
              "type": "kmarkdown",
              "content": "*" + sender + "*"
            }
          },
          {
            "type": "section",
            "text": {
              "type": "kmarkdown",
              "content": "**邀约详情**"
            }
          },
          {
            "type": "section",
            "text": {
              "type": "kmarkdown",
              "content": "**时间：**"+time +"\n**地点：**" + address
            }
          },
          {
            "type": "context",
            "elements": [
              {
                "type": "kmarkdown",
                "content": "***留言：****"+ note + "*"
              }
            ]
          },
          {
            "type": "divider"
          },
            {
                "type": "action-group",
                "elements": [
                    {
                        "type": "button",
                        "theme": "primary",
                        "value": accept_value,
                        "click": "return-val",
                        "text": {
                            "type": "plain-text",
                            "content": "接受"
                        }
                    },
                    {
                        "type": "button",
                        "theme": "danger",
                        "value": reject_value,
                        "click": "return-val",
                        "text": {
                            "type": "plain-text",
                            "content": "拒绝"
                        }
                    }
                ]
            }
        ]
      }]
    j = json.dumps(j,ensure_ascii=False, indent=4)
    return j

def getMiniDateDisEnableContet(content,m):
    EP = content.split("发起人：")[0].strip()
    sender = content.split("发起人：", 1)[1].split("接收人：", 1)[0].strip()
    recever_name = content.split("接收人：", 1)[1].split("时间：", 1)[0].strip()
    time = content.split("时间：", 1)[1].split("地点：", 1)[0].strip()
    address = content.split("地点：", 1)[1].split("留言：", 1)[0].strip()
    note = content.split("留言：", 1)[1].split("icon：", 1)[0].strip()
    icon_src = content.split("icon：", 1)[1].strip()

    j = [{
        "type": "card",
        "size": "sm",
        "theme": "info",
        "modules": [
          {
            "type": "header",
            "text": {
              "type": "plain-text",
              "content": "私约邀请·" + EP
            }
          },
          {
            "type": "divider"
          },
          {
            "type": "section",
            "text": {
              "type": "kmarkdown",
              "content": "**邀请人**"
            }
          },
          {
            "type": "section",
            "mode": "left",
            "accessory": {
              "type": "image",
              "src": icon_src,
              "circle": True
            },
            "text": {
              "type": "kmarkdown",
              "content": "*" + sender + "*"
            }
          },
          {
            "type": "section",
            "text": {
              "type": "kmarkdown",
              "content": "**邀约详情**"
            }
          },
          {
            "type": "section",
            "text": {
              "type": "kmarkdown",
              "content": "**时间：**"+time +"\n**地点：**" + address
            }
          },
          {
            "type": "context",
            "elements": [
              {
                "type": "kmarkdown",
                "content": "***留言：****"+ note + "*"
              }
            ]
          },
          {
            "type": "divider"
          },
          {
            "type": "action-group",
            "elements": [
              {
                "type": "button",
                "theme": "secondary",
                "value": "done",
                "text": {
                  "type": "plain-text",
                  "content": m
                }
              }
            ]
          }
        ]
      }]

    j = json.dumps(j,ensure_ascii=False, indent=4)
    return j

def getImgTemplate(img_src):
    p_json = [{
            "type": "card",
            "theme": "warning",
            "size": "lg",
            "modules": [
                {
                    "type": "container",
                    "elements": [
                        {
                            "type": "image",
                            "src": img_src
                        }
                    ]
                }
            ]
        }]
    j = json.dumps(p_json, ensure_ascii=False, indent=4)
    return j

def getWashWallContet(content,EP,sender_name,wish,time, name="",type=0):

    if type == 0:
        accept_value = content + "\n发布人：" + name
        button_theme = "primary"
        button_txt = "摘取"
    else:
        accept_value = "done"
        button_theme = "secondary"
        button_txt = "已被摘取"

    j = [{
            "type": "card",
            "size": "sm",
            "theme": "warning",
            "modules": [
              {
                "type": "header",
                "text": {
                  "type": "plain-text",
                  "content": "心愿·"+EP
                }
              },
              {
                "type": "divider"
              },
              {
                "type": "section",
                "text": {
                  "type": "kmarkdown",
                  "content": "**"+wish+"**"
                }
              },
              {
                "type": "context",
                "elements": [
                  {
                    "type": "plain-text",
                    "content": name + " 在 "+ time +" 发布"
                  }
                ]
              },
              {
                "type": "action-group",
                "elements": [
                  {
                    "type": "button",
                    "theme": button_theme,
                    "click":"return-val",
                    "value": accept_value,
                    "text": {
                      "type": "plain-text",
                      "content": button_txt
                    }
                  }
                ]
              }
            ]
          }]

    j = json.dumps(j,ensure_ascii=False, indent=4)
    return j

def getWashWallDisEnableContent(content):
    EP = content.split("心愿·", 1)[1].split("署名：", 1)[0].strip()
    sender_name = content.split("署名：", 1)[1].split("内容：", 1)[0].strip()
    wish = content.split("内容：", 1)[1].split("时间：", 1)[0].strip()
    time = content.split("时间：", 1)[1].split("发布人：", 1)[0].strip()

    j = [{
        "type": "card",
        "size": "lg",
        "theme": "warning",
        "modules": [
            {
                "type": "header",
                "text": {
                    "type": "plain-text",
                    "content": "心愿·" + EP
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "plain-text",
                    "content": wish
                }
            },
            {
                "type": "section",
                "accessory": {},
                "text": {
                    "type": "paragraph",
                    "cols": 2,
                    "fields": [
                        {
                            "type": "kmarkdown",
                            "content": "**发布人**"
                        },
                        {
                            "type": "kmarkdown",
                            "content": "**时间**"
                        },
                        {
                            "type": "kmarkdown",
                            "content": sender_name
                        },
                        {
                            "type": "kmarkdown",
                            "content": time
                        }
                    ]
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "action-group",
                "elements": [
                    {
                        "type": "button",
                        "theme": "secondary",
                        "value": "done",
                        "text": {
                            "type": "plain-text",
                            "content": "已被摘取"
                        }
                    }
                ]
            }
        ]
    }]

    j = json.dumps(j, ensure_ascii=False, indent=4)
    return j

def getNoteTemplate(content,sender,receiver):
    j = [{
            "type": "card",
            "size": "sm",
            "theme": "info",
            "modules": [
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "kmarkdown",
                            "content": "***To ****"+ receiver +"*"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "kmarkdown",
                        "content": "*"+content+"*"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "kmarkdown",
                            "content": "          ***From ****"+ sender +"*"
                        }
                    ]
                }
            ]
        }]

    j = json.dumps(j, ensure_ascii=False, indent=4)
    return j

def getPublicNoteTemplate(content,sender,time):
    j = [{
            "type": "card",
            "theme": "secondary",
            "size": "sm",
            "modules": [
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "kmarkdown",
                            "content": "***"+sender+"***   "
                        },
                        {
                            "type": "plain-text",
                            "content": " " + time
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "plain-text",
                        "content": content
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "kmarkdown",
                            "content": "*留言板块出现了一则新消息*"
                        }
                    ]
                }
            ]
        }]

    j = json.dumps(j, ensure_ascii=False, indent=4)
    return j

def getMusicTemplate(note,sender,recevier,time):

    j = [{
        "type": "card",
        "size": "sm",
        "theme": "info",
        "modules": [
          {
            "type": "header",
            "text": {
              "type": "plain-text",
              "content": "点歌台"
            }
          },
          {
            "type": "divider"
          },
          {
            "type": "context",
            "elements": [
              {
                "type": "kmarkdown",
                "content": time + " 来自 *" + sender + "* 的一首歌，提醒 *@"+ recevier + "* 收听"
              }
            ]
          },
          {
            "type": "section",
            "text": {
              "type": "kmarkdown",
              "content": "**" + note + "**"
            }
          }
        ]
      }]
    j = json.dumps(j, ensure_ascii=False, indent=4)
    return j


def getGiftTemplate(sender,receiver,gift,note,time,imgs):

    j = [{
        "type": "card",
        "size": "sm",
        "theme": "info",
        "modules": [
          {
            "type": "header",
            "text": {
              "type": "plain-text",
              "content": time + " 来自 "+ sender +" 的礼物"
            }
          },
          {
            "type": "context",
            "elements": [
              {
                "type": "plain-text",
                "content": "To " + receiver
              }
            ]
          },
          {
            "type": "context",
            "elements": [
              {
                "type": "plain-text",
                "content": note
              }
            ]
          },
          {
            "type": "context",
            "elements": [
              {
                "type": "plain-text",
                "content": "礼物：" + gift
              }
            ]
          },
          {
                "type": "divider",
          }

        ]
      }
    ]

    if imgs:
        for src in imgs:
            d = {
                "type": "container",
                "elements": [
                    {
                        "type": "image",
                        "src": src
                    }
                ]
            }
            j[0]['modules'].append(d)

    j = json.dumps(j, ensure_ascii=False, indent=4)
    return j

def getLetterTemplate(sender,content,imgs):
   j =[{
        "type": "card",
        "theme": "info",
        "size": "lg",
        "modules": [
          {
            "type": "section",
            "text": {
              "type": "plain-text",
              "content": content
            }
          },
          {
            "type": "context",
            "elements": [
              {
                "type": "kmarkdown",
                "content": "  *你的信箱里有一封来自 **" + sender + "** 的信*"
              }
            ]
          },
          {
            "type": "divider"
          }
        ]
      }
    ]

   if imgs:
       for src in imgs:
           d = {
               "type": "container",
               "elements": [
                   {
                       "type": "image",
                       "src": src
                   }
               ]
           }
           j[0]['modules'].append(d)

   j = json.dumps(j, ensure_ascii=False, indent=4)
   return j