# -*- coding: utf-8 -*-
"""Xのトレンド8位までの名前を index.html の在庫に当てる（feedback_x_trend_match_inventory）。
「いま買える枠」があるものだけ拾う。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

TODAY = "2026-09-06"
# トレンド1〜8位から、在庫に当たりうる固有名詞を抜き出したもの
WORDS = {
    "西武": "3位 れおほー（埼玉西武ライオンズ）",
    "ライオンズ": "3位 れおほー（埼玉西武ライオンズ）",
    "Liella": "8位 #Liella_結女体育祭_Day2",
    "リエラ": "8位 #Liella_結女体育祭_Day2",
    "ラブライブ": "8位 #Liella_結女体育祭_Day2（関連）",
    "セントウル": "6位 セントウルS",
    "紫苑ステークス": "14位 紫苑ステークス",
    "学マス": "10位 #学マス標ツアー_福岡公演_DAY2",
    "学園アイドルマスター": "10位 #学マス標ツアー_福岡公演_DAY2",
}

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))


def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), t.get("date")
    return not ((not sd or sd <= TODAY) and (d or "") < TODAY)


for w, label in WORDS.items():
    hits = []
    for e in EVENTS:
        blob = " ".join(str(e.get(k) or "") for k in ("artist", "name", "venue", "dateLabel"))
        if w.lower() in blob.lower():
            vis = [t for t in (e.get("tickets") or []) if visible(t)]
            if vis:
                hits.append((e, vis))
    if hits:
        print("")
        print("=== 「%s」 %s ＝ %d件 ===" % (w, label, len(hits)))
        for e, vis in hits:
            print("  id=%-5d %s @%s 公演%s [%s]"
                  % (e["id"], (e.get("artist") or "")[:40], (e.get("venue") or "")[:30],
                     e.get("date"), e.get("genre")))
            for t in vis:
                mark = "（予定枚数終了）" if t.get("soldout") else ""
                print("      枠 %s （〜%s）%s" % (t.get("type"), t.get("date"), mark))
