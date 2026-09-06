# -*- coding: utf-8 -*-
"""9/7発売の各枠について、券種名の「（県名 M/D公演）」から本当の公演地を取り直す。
🚨エントリの prefecture はツアー全体の県なので、その枠の公演地とは違う（今回の素材の間違い）。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

DAY = "2026-09-07"
PREFS = ("北海道 青森 岩手 宮城 秋田 山形 福島 茨城 栃木 群馬 埼玉 千葉 東京 神奈川 "
         "新潟 富山 石川 福井 山梨 長野 岐阜 静岡 愛知 三重 滋賀 京都 大阪 兵庫 奈良 "
         "和歌山 鳥取 島根 岡山 広島 山口 徳島 香川 愛媛 高知 福岡 佐賀 長崎 熊本 大分 "
         "宮崎 鹿児島 沖縄 全国").split()

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

for e in EVENTS:
    for t in e.get("tickets") or []:
        if t.get("startDate") != DAY:
            continue
        tt = t.get("type") or ""
        mm = re.search(r"（([^（）]*?)\s*[R\d][^（）]*?公演）", tt)
        seg = mm.group(1) if mm else ""
        found = [p for p in PREFS if p in seg]
        hm = re.search(r"(\d{1,2}):(\d{2})発売", tt)
        time = "%02d:%s" % (int(hm.group(1)), hm.group(2)) if hm else "??:??"
        senko = "（先行）" if ("先行" in tt or "プレリザーブ" in tt or "プリセール" in tt) else ""
        print("%s %s／%s%s" % (time, e.get("artist") or "", "・".join(found) or "?", senko))
        print("      エントリのprefecture=%s   券種=%s" % (e.get("prefecture"), tt))
