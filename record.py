import json
from collections import defaultdict

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
        *{{margin:0;padding:0;box-sizing:border-box;font-family:Microsoft YaHei,sans-serif}}
        body{{background:#f7f6f3;color:#333;line-height:1.7;padding:20px;max-width:1200px;margin:0 auto}}
        .stat{{background:#fff;padding:20px 30px;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,.08);margin-bottom:30px}}
        .stat h1{{font-size:24px;color:#b85b5b;margin-bottom:15px;border-left:5px solid #b85b5b;padding-left:10px}}
        .stat-info{{display:flex;gap:30px;flex-wrap:wrap;font-size:16px}}
        .stat-item{{padding:5px 10px;background:#f9f1f0;border-radius:6px}}

        /* 目录样式 */
        .catalog{{background:#fff;padding:20px 30px;border-radius:12px;margin-bottom:30px}}
        .catalog h2{{font-size:20px;margin-bottom:15px;color:#666}}
        .catalog-main{{list-style:none;margin-bottom:12px}}
        .catalog-sub{{list-style:none;margin-left:20px;margin-bottom:6px;font-size:14px}}
        .catalog a{{color:#b85b5b;text-decoration:none;padding:4px 8px;border-radius:4px;display:inline-block}}
        .catalog a:hover{{background:#f9f1f0}}

        .ep{{font-size:22px;background:#b85b5b;color:#fff;padding:10px 20px;border-radius:8px;margin:30px 0 20px}}
        .card{{background:#fff;border-radius:10px;padding:20px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,.06)}}
        .card-header{{border-bottom:1px solid #eee;padding-bottom:10px;margin-bottom:15px;color:#666;font-size:14px}}
        .content{{white-space:pre-wrap;font-size:15px;line-height:1.9}}
        .speaker{{color:#b85b5b;font-weight:bold;margin-right:8px}}
        .empty{{color:#999;font-style:italic}}
    </style>
</head>
<body>
    <div class="stat">
        <h1>{title_name} · {pName} 个人记录</h1>
        <div class="stat-info">
            <span class="stat-item">总场次：{total_plays} 场</span>
            <span class="stat-item">总字数：{total_words} 字</span>
        </div>
    </div>

    <!-- 二级目录 -->
    <div class="catalog">
        <h2>📑 目录</h2>
        {''.join([
        f'<ul class="catalog-main"><li><a href="#{ep}">📂 {ep}（共{len(ls)}场）</a><ul class="catalog-sub">' +
        ''.join([f'<li><a href="#{p["anchor_id"]}">· {p["channel_name"]}</a></li>' for p in ls]) +
        '</ul></li></ul>'
        for ep, ls in sorted(ep_groups.items())
    ])}
    </div>
'''

    # 逐 EP 生成戏录
    for ep in sorted(ep_groups.keys()):
        html += f'<h2 class="ep" id="{ep}">{ep}</h2>\n'
        for play in ep_groups[ep]:
            anchor_id = play["anchor_id"]
            channel = play["channel_name"]
            time = play["last_time"]
            person = play["current_person"]
            status = "已完成" if play["is_finished"] else "进行中"
            content_list = play["content"]

            html += f'''
    <div class="card" id="{anchor_id}">
        <div class="card-header">
            {channel}｜{time}｜{status}
        </div>
        <div class="content">
            '''
            if not content_list:
                html += '<p class="empty">暂无戏录内容</p>'
            else:
                for text in content_list:
                    lines = [l.strip() for l in text.split("\n") if l.strip()]
                    for line in lines:
                        if line in ("观荐", "马克"):
                            html += f'<p><span class="speaker">{line}：</span></p>'
                        else:
                            html += f"<p>{line}</p>"
            html += "</div></div>"

    html += "</body></html>"

    # 6. 写入文件
    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    msg = f"✅ 生成成功！\n📊 统计：总场数 {total_plays}，总字数 {total_words}"
    return msg