# 语擦机器人

KOOK机器人，用于恋综语擦辅助。

## 快速开始

```bash
# 安装依赖
pip install khl requests

# 运行机器人
python main.py
```

## 功能特性

### 管理员功能
- 创建/清空恋综
- 绑定/移除个人频道
- 批量创建 EP 频道
- 私约邀请管理
- 踩点活动
- 心动信管理
- 国王游戏出题
- 折手指游戏
- 数据统计
- 超时检查与回戏提醒

### 玩家互动
- 骰子（.rd80、.r3d6+2、.ra50）
- 传纸条（To角色名 内容）
- 送礼物
- 点歌
- 发布心愿
- 发布公共留言

### 档案与记录
- 个人档案
- 回戏档案
- 生成戏录（HTML）
- 导出频道记录

## 指令示例

```
创建·恋综名称
绑定·恋综名称 角色名 @玩家 @角色组
通讯·角色A&角色B
私约·EP1
To观荐 你好呀
.ra智力80
折手指·新建
生成戏录·恋综名称 角色名
统计
```

## 数据存储

```
./data/
├── config.json          # 机器人 Token
├── data.json           # 服务器映射
├── 恋综名.json         # 恋综配置
└── 恋综名/
    ├── 玩家名.json     # 个人档案
    └── letter.json     # 心动信
```

## 项目结构

| 文件 | 说明 |
|------|------|
| main.py | 机器人入口，命令路由，核心逻辑 |
| template.py | KOOK 卡片消息模板 |
| record.py | HTML 戏录生成器 |
| utils.py | 时间计算工具 |
| dice_main.py | 骰子引擎 |
| 使用手册.md | 完整指令手册 |

## 技术栈

- Python 3.9+
- [khl](https://github.com/chatomin/khl) - KOOK API SDK
- requests - HTTP 请求
- onedice - 骰子引擎
