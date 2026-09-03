# -*- coding: utf-8 -*-
"""振り分け前に、新着プールの割り当て一覧を logs に残す（後からユーザーが見るため）。"""
import json, re, io

HOLD = {6397}

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
pool = [e for e in events if e.get("genre") == "new"]

buf = ["# 振り分けログ 2026-09-04（朝の便）", "",
       "別エージェントがぴあカテゴリとの整合を独立検証。指摘8件のうち4件を直してから振り分けた。",
       "（6437・6442 → talkshow / 6477 → classic / 6395 → hougaku）", "",
       "⚠️ id6397「GOOD DAY KYOTO」は kpop に読み替えるか相談中のため、振り分けず新着に残している。", ""]
n = 0
for e in sorted(pool, key=lambda x: x.get("id")):
    if e.get("id") in HOLD:
        continue
    u = (e.get("links") or {}).get("pia") or ""
    buf.append("- **id%s %s** -> %s" % (e.get("id"), e.get("name"), e.get("_genre")))
    buf.append("  %s / %s" % (e.get("dateLabel"), u))
    n += 1
io.open("logs/assigned_2026-09-04.md", "w", encoding="utf-8").write("\n".join(buf))
print("POOL=%d  LOGGED=%d  HOLD=%d" % (len(pool), n, len(HOLD)))
