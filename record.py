import json
from collections import defaultdict

FAIL = "❌ "

def generateRecord(JSON_FILE,OUTPUT_HTML):
    # 1. 读取 JSON 文件
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 2. 基础数据
    title_name = data["sName"]
    pName = data["name"]
    plays = list(data["details"].values())

    # 3. 统计：总场数、总字数
    total_plays = len(plays)
    total_words = 0
    for play in plays:
        for text in play["content"]:
            total_words += len(text.strip())

    # 4. 按 EP 分组（给每场戏加唯一ID，用于锚点跳转）
    ep_groups = defaultdict(list)
    for play_idx, play in enumerate(plays):
        ep = play["EP"]
        play["anchor_id"] = f"play_{play_idx}"  # 唯一跳转ID
        ep_groups[ep].append(play)

    # 5. 生成 HTML 内容
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{title_name}·{pName} - 戏录</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family:"PingFang SC","Microsoft YaHei",-apple-system,BlinkMacSystemFont,sans-serif;background:#f5f5f7;color:#1d1d1f;line-height:1.8;padding:40px 20px}}
        .container{{max-width:900px;margin:0 auto}}

        .header{{text-align:center;margin-bottom:50px}}
        .header h1{{font-size:28px;font-weight:600;color:#1d1d1f;letter-spacing:2px}}
        .header .subtitle{{font-size:14px;color:#86868b;margin-top:8px}}
        .stat-bar{{display:flex;justify-content:center;gap:40px;margin-top:24px}}
        .stat-item{{text-align:center}}
        .stat-item .num{{font-size:32px;font-weight:700;color:#0071e3}}
        .stat-item .label{{font-size:12px;color:#86868b;text-transform:uppercase;letter-spacing:1px;margin-top:4px}}

        .catalog{{background:#fff;border-radius:16px;padding:28px 32px;margin-bottom:32px;box-shadow:0 2px 12px rgba(0,0,0,.04)}}
        .catalog h2{{font-size:16px;font-weight:600;color:#1d1d1f;margin-bottom:16px}}
        .catalog-ep{{margin-bottom:12px}}
        .catalog-ep-title{{font-size:14px;font-weight:600;color:#1d1d1f;margin-bottom:8px}}
        .catalog a{{color:#0071e3;text-decoration:none;font-size:14px;padding:4px 10px;border-radius:6px;display:inline-block;margin:2px;background:#f5f5f7;transition:all .2s}}
        .catalog a:hover{{background:#0071e3;color:#fff}}

        .ep-title{{font-size:18px;font-weight:600;color:#fff;background:linear-gradient(135deg,#1d1d1f,#3a3a3c);padding:14px 24px;border-radius:12px;margin:36px 0 20px;letter-spacing:1px}}

        .card{{background:#fff;border-radius:16px;padding:24px 28px;margin-bottom:20px;box-shadow:0 2px 12px rgba(0,0,0,.04);transition:transform .2s}}
        .card:hover{{transform:translateY(-2px);box-shadow:0 4px 20px rgba(0,0,0,.08)}}
        .card-meta{{font-size:13px;color:#86868b;padding-bottom:12px;border-bottom:1px solid #f5f5f7;margin-bottom:16px;display:flex;justify-content:space-between}}
        .card-meta .channel{{font-size:16px;font-weight:600;color:#1d1d1f}}
        .card-meta .status{{padding:2px 8px;border-radius:4px;font-size:11px}}
        .status.done{{background:#d1f7d1;color:#006600}}
        .status.active{{background:#fff3cd;color:#856404}}

        .content{{font-size:14px;color:#1d1d1f}}
        .content p{{margin-bottom:8px}}
        .speaker{{font-weight:600;color:#0071e3;margin-right:4px}}
        .empty{{color:#86868b;font-style:italic;text-align:center;padding:20px}}

        .divider{{height:1px;background:linear-gradient(90deg,transparent,#d2d2d7,transparent);margin:40px 0}}

        @media (max-width:600px){{
            body{{padding:20px 12px}}
            .header h1{{font-size:22px}}
            .stat-bar{{gap:20px}}
            .stat-item .num{{font-size:24px}}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{pName}</h1>
            <p class="subtitle">{title_name} · 个人戏录</p>
            <div class="stat-bar">
                <div class="stat-item">
                    <div class="num">{total_plays}</div>
                    <div class="label">场次</div>
                </div>
                <div class="stat-item">
                    <div class="num">{total_words}</div>
                    <div class="label">字数</div>
                </div>
            </div>
        </div>

        <div class="catalog">
            <h2>📑 目录</h2>
            {''.join([
                f'<div class="catalog-ep"><div class="catalog-ep-title">{ep}</div><div>' +
                ''.join([f'<a href="#{p["anchor_id"]}">{p["channel_name"]}</a>' for p in ls]) +
                '</div></div>'
                for ep, ls in sorted(ep_groups.items())
            ])}
        </div>
'''

    # 逐 EP 生成戏录
    for ep in sorted(ep_groups.keys()):
        html += f'<div class="ep-title" id="{ep}">{ep}</div>\n'
        for play in ep_groups[ep]:
            anchor_id = play["anchor_id"]
            channel = play["channel_name"]
            is_finished = play["is_finished"]
            status_class = "done" if is_finished else "active"
            status_text = "已完成" if is_finished else "进行中"
            content_list = play["content"]

            html += f'''
        <div class="card" id="{anchor_id}">
            <div class="card-meta">
                <span class="channel">{channel}</span>
                <span class="status {status_class}">{status_text}</span>
            </div>
            <div class="content">
            '''
            if not content_list:
                html += '<p class="empty">暂无戏录内容</p>'
            else:
                for text in content_list:
                    lines = [l.strip() for l in text.split("\n") if l.strip()]
                    if lines:
                        # 第一行是发言角色名
                        html += f'<p><span class="speaker">{lines[0]}：</span></p>'
                        # 后续行是发言内容
                        for line in lines[1:]:
                            html += f"<p>{line}</p>"
            html += "</div></div>"

    html += '''
        <div class="divider"></div>
    </div>
</body>
</html>'''

    # 6. 写入文件
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    msg = f"✅ 生成成功！\n📊 统计：总场数 {total_plays}，总字数 {total_words}"
    return msg

def generateSeriesRecord(sName, OUTPUT_HTML):
    """生成恋综纪念册，面向整个恋综的所有戏录"""
    import os

    series_path = f"./data/{sName}/"
    if not os.path.exists(series_path):
        return FAIL + f"恋综 [{sName}] 不存在"

    # 收集所有玩家的戏录数据
    all_plays = {}  # {(channel_name, EP): play_data}
    player_stats = {}  # {player_name: {"plays": count, "words": count}}

    for filename in os.listdir(series_path):
        if filename.endswith(".json") and filename not in ["letter.json"]:
            player_name = filename.replace(".json", "")
            filepath = os.path.join(series_path, filename)

            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)

                player_stats[player_name] = {"plays": 0, "words": 0}

                for channel_id, play in data.get("details", {}).items():
                    key = (play["channel_name"], play["EP"])
                    if key not in all_plays:
                        all_plays[key] = play.copy()
                        all_plays[key]["players"] = []
                    if player_name not in all_plays[key]["players"]:
                        all_plays[key]["players"].append(player_name)
                        player_stats[player_name]["plays"] += 1

                    for text in play.get("content", []):
                        player_stats[player_name]["words"] += len(text.strip())

            except Exception as e:
                continue

    # 按 EP 分组
    ep_groups = defaultdict(list)
    for (channel_name, ep), play in all_plays.items():
        play["channel_name"] = channel_name
        play["EP"] = ep
        play["anchor_id"] = f"play_{channel_name}_{ep}".replace(" ", "_")
        ep_groups[ep].append(play)

    # 统计
    total_plays = len(all_plays)
    total_players = len(player_stats)
    total_words = sum(s["words"] for s in player_stats.values())

    # 生成 HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{sName} - 恋综纪念册</title>
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        body{{font-family:"PingFang SC","Microsoft YaHei",-apple-system,BlinkMacSystemFont,sans-serif;background:#f5f5f7;color:#1d1d1f;line-height:1.8;padding:40px 20px}}
        .container{{max-width:900px;margin:0 auto}}

        .header{{text-align:center;margin-bottom:50px}}
        .header h1{{font-size:28px;font-weight:600;color:#1d1d1f;letter-spacing:2px}}
        .header .subtitle{{font-size:14px;color:#86868b;margin-top:8px}}
        .stat-bar{{display:flex;justify-content:center;gap:40px;margin-top:24px}}
        .stat-item{{text-align:center}}
        .stat-item .num{{font-size:32px;font-weight:700;color:#0071e3}}
        .stat-item .label{{font-size:12px;color:#86868b;text-transform:uppercase;letter-spacing:1px;margin-top:4px}}

        .catalog{{background:#fff;border-radius:16px;padding:28px 32px;margin-bottom:32px;box-shadow:0 2px 12px rgba(0,0,0,.04)}}
        .catalog h2{{font-size:16px;font-weight:600;color:#1d1d1f;margin-bottom:16px}}
        .catalog-ep{{margin-bottom:12px}}
        .catalog-ep-title{{font-size:14px;font-weight:600;color:#1d1d1f;margin-bottom:8px}}
        .catalog a{{color:#0071e3;text-decoration:none;font-size:14px;padding:4px 10px;border-radius:6px;display:inline-block;margin:2px;background:#f5f5f7;transition:all .2s}}
        .catalog a:hover{{background:#0071e3;color:#fff}}

        .ep-title{{font-size:18px;font-weight:600;color:#fff;background:linear-gradient(135deg,#1d1d1f,#3a3a3c);padding:14px 24px;border-radius:12px;margin:36px 0 20px;letter-spacing:1px}}

        .card{{background:#fff;border-radius:16px;padding:24px 28px;margin-bottom:20px;box-shadow:0 2px 12px rgba(0,0,0,.04);transition:transform .2s}}
        .card:hover{{transform:translateY(-2px);box-shadow:0 4px 20px rgba(0,0,0,.08)}}
        .card-meta{{font-size:13px;color:#86868b;padding-bottom:12px;border-bottom:1px solid #f5f5f7;margin-bottom:16px;display:flex;justify-content:space-between}}
        .card-meta .channel{{font-size:16px;font-weight:600;color:#1d1d1f}}
        .card-meta .players{{font-size:12px;color:#86868b}}
        .card-meta .status{{padding:2px 8px;border-radius:4px;font-size:11px}}
        .status.done{{background:#d1f7d1;color:#006600}}
        .status.active{{background:#fff3cd;color:#856404}}

        .content{{font-size:14px;color:#1d1d1f}}
        .content p{{margin-bottom:8px}}
        .speaker{{font-weight:600;color:#0071e3;margin-right:4px}}
        .empty{{color:#86868b;font-style:italic;text-align:center;padding:20px}}

        .divider{{height:1px;background:linear-gradient(90deg,transparent,#d2d2d7,transparent);margin:40px 0}}

        @media (max-width:600px){{
            body{{padding:20px 12px}}
            .header h1{{font-size:22px}}
            .stat-bar{{gap:20px}}
            .stat-item .num{{font-size:24px}}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{sName}</h1>
            <p class="subtitle">恋综纪念册</p>
            <div class="stat-bar">
                <div class="stat-item">
                    <div class="num">{total_plays}</div>
                    <div class="label">场次</div>
                </div>
                <div class="stat-item">
                    <div class="num">{total_players}</div>
                    <div class="label">角色</div>
                </div>
                <div class="stat-item">
                    <div class="num">{total_words}</div>
                    <div class="label">字数</div>
                </div>
            </div>
        </div>

        <div class="catalog">
            <h2>📑 目录</h2>
            {''.join([
                f'<div class="catalog-ep"><div class="catalog-ep-title">{ep}</div><div>' +
                ''.join([f'<a href="#{p["anchor_id"]}">{p["channel_name"]}</a>' for p in ls]) +
                '</div></div>'
                for ep, ls in sorted(ep_groups.items())
            ])}
        </div>
'''

    # 逐 EP 生成戏录
    for ep in sorted(ep_groups.keys()):
        html += f'<div class="ep-title" id="{ep}">{ep}</div>\n'
        for play in ep_groups[ep]:
            anchor_id = play["anchor_id"]
            channel = play["channel_name"]
            players = play["players"]
            is_finished = play["is_finished"]
            status_class = "done" if is_finished else "active"
            status_text = "已完成" if is_finished else "进行中"
            content_list = play["content"]

            html += f'''
        <div class="card" id="{anchor_id}">
            <div class="card-meta">
                <span class="channel">{channel}</span>
                <span class="status {status_class}">{status_text}</span>
            </div>
            <div class="card-meta">
                <span class="players">{' / '.join(players)}</span>
            </div>
            <div class="content">
            '''
            if not content_list:
                html += '<p class="empty">暂无戏录内容</p>'
            else:
                for text in content_list:
                    lines = [l.strip() for l in text.split("\n") if l.strip()]
                    if lines:
                        html += f'<p><span class="speaker">{lines[0]}：</span></p>'
                        for line in lines[1:]:
                            html += f"<p>{line}</p>"
            html += "</div></div>"

    html += '''
        <div class="divider"></div>
    </div>
</body>
</html>'''

    # 写入文件
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    msg = f"✅ 纪念册生成成功！\n📊 统计：总场数 {total_plays}，角色 {total_players}，总字数 {total_words}"
    return msg