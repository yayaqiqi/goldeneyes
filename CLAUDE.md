# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

一个 KOOK（原开黑啦）聊天机器人，用于管理恋综角色扮演社区的互动。使用 Python 编写，通过 `khl` 库与 KOOK API 交互。代码库全部使用中文——包括用户界面文本、命令语法、数据键名和注释。

## 运行机器人

```bash
pip install khl requests
python main.py
```

本项目没有构建系统、测试框架、代码检查工具或 CI/CD 配置。`test.py` 是空文件。

## 架构

**单文件主体**：`main.py`（约 1200 行）包含所有机器人逻辑、命令路由和 KOOK API 交互。

**命令路由**：通过 `if/elif` 链和 `message.startswith(...)` 进行前缀匹配分发命令，前缀为中文命令如 `创建·`、`绑定·`、`私约·`、`礼物·`、`To` 等。用户输入通过中文分隔符（`发起人：`、`接收人：`、`署名：`、`内容：`）进行解析。

**事件处理**：
- `@bot.on_message()` — 处理所有文本/卡片消息
- `@bot.on_event(EventTypes.MESSAGE_BTN_CLICK)` — 处理按钮点击事件（接受/拒绝邀请、选取心愿）
- `@bot.task.add_cron(hour=12, minute=0)` — 每日定时任务，执行清理、超时检查和提醒

**KOOK API 访问**：混合使用 `khl` SDK 方法和直接通过 `requests` 调用 `https://www.kookapp.cn/api/v3/...`。

## 关键文件

- `main.py` — 机器人入口和全部命令逻辑
- `template.py` — KOOK 卡片消息 JSON 构建器（邀请、礼物、点歌、信件、心愿、公共留言）
- `record.py` — 从玩家 JSON 数据生成带样式的 HTML 戏录
- `utils.py` — 时间工具函数（计算小时差，用于超时检测）

## 数据存储

所有状态以 JSON 文件形式保存在 `./data/` 目录下，没有使用数据库：

- `config.json` — 机器人 Token（敏感信息，不可提交到版本控制）
- `data.json` — 服务器到系列的映射（`{guild_id: series_name}`）
- `<系列名>.json` — 每个系列的配置（solos、roles、parents、user_ids）
- `<系列名>/<玩家名>.json` — 个人档案记录（对戏详情、字数统计、EP 追踪）
- `<系列名>/letter.json` — 该系列的心动信数据

## 备份

`beifen/main.py` 是机器人的旧版备份（约 847 行），功能较少。除非明确要求，否则不要修改此文件。

## 开发约定

- Python 3.9
- 代码中没有类型提示和文档字符串
- 命令和数据键名使用中文——添加新功能时请保持这一约定
- KOOK 卡片消息使用 `khl.card` 模块构建富文本消息 JSON
