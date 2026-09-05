# -*- coding: utf-8 -*-
"""Fableが書いた8本を1本ずつのファイルに割って、tools/x_check.py に通す。

🚨 x_check.py は「1ファイル＝1投稿」の想定なので、見出し付きのまとめファイルをそのまま渡すと
   1行目チェックで落ちる（2026-09-05）。
"""
import re, io, os, subprocess, sys

SRC = "tmp/x_draft_0905.md"
OUT = "tmp/x_posts_0905"
os.makedirs(OUT, exist_ok=True)

s = io.open(SRC, encoding="utf-8").read()
parts = re.findall(r"###\s*(\d+)本目[：:]\s*(.+?)\n+```\n(.*?)\n```", s, re.S)
print("見つかった投稿: %d本" % len(parts))

buf = []
for n, title, body in parts:
    p = os.path.join(OUT, "x%s.txt" % n)
    io.open(p, "w", encoding="utf-8").write(body.strip() + "\n")
    r = subprocess.run([sys.executable, "tools/x_check.py", p],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    ok = "指摘あり 0本" in (r.stdout or "") or "❌" not in (r.stdout or "")
    buf.append("=" * 60)
    buf.append("%s %s本目：%s  （%d字）" % ("OK  " if ok else "🚨NG", n, title.strip(), len(body.strip())))
    for line in (r.stdout or "").splitlines():
        if "❌" in line or "⚠" in line:
            buf.append("     " + line.strip())

# 台本の必須項目を自前でも見る
buf.append("")
buf.append("=" * 60)
buf.append("【台本の必須項目】")
for n, title, body in parts:
    b = body.strip()
    ng = []
    if not b.startswith('OSHINAVIの"9/6チケット発売"ピックアップ🎫'):
        ng.append("1行目が違う")
    if "#OSHINAVI" not in b or "#明日発売" not in b or "#チケット" not in b:
        ng.append("タグが欠けている")
    if "▼チケット情報はこちら" not in b:
        ng.append("CTAが無い")
    if b.count("oshinavi.jp") < 2:
        ng.append("oshinavi.jp が前半と末尾の2回入っていない（%d回）" % b.count("oshinavi.jp"))
    if "https://" in b:
        ng.append("https:// を書いている")
    for word in ("あんた", "生で浴びる", "押さえる", "両方おさえる"):
        if word in b:
            ng.append("禁止語「%s」" % word)
    # 「。」の直後が改行か（「モーニング娘。」だけ例外）
    for m in re.finditer(r"。(?!\n)(.)", b):
        around = b[max(0, m.start() - 8):m.start() + 1]
        if "モーニング娘。" in around:
            continue
        ng.append("「。」の直後が改行でない: …%s" % b[max(0, m.start() - 12):m.start() + 3].replace("\n", "／"))
        break
    buf.append("%s %s本目 %s" % ("OK  " if not ng else "🚨NG", n, "／".join(ng) if ng else ""))

io.open("tmp/x_split_check_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("wrote tmp/x_split_check_0905.txt")
