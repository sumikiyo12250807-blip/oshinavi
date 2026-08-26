# -*- coding: utf-8 -*-
"""明日(8/27)発売のまとめ投稿用データ。ジャンル別×その中で時間順に並べる。
feedback_x_post_method_0825 ＝名前をそのまま載せる／件数は書かない／時間だけのフラットな並びにしない。
🚨会員限定の先行は「会員限定」と分かる形で出す（feedback_x_senko_is_conditional）。"""
import re
import json
import sys
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")

TARGET, MD = "2026-08-27", "8/27"
GN = {"jpop": "J-POP・ロック", "enka": "演歌・歌謡", "classic": "クラシック", "jazz": "ジャズ",
      "owarai": "お笑い・落語", "engeki": "演劇・ミュージカル", "kpop": "K-POP",
      "yougaku": "海外アーティスト", "fes": "フェス", "kids": "こども向け", "sports": "スポーツ",
      "dento": "伝統芸能", "art": "アート", "dinnershow": "ディナーショー", "aisatsu": "舞台挨拶",
      "seiyuu": "声優・アニメ", "gourmet": "グルメ", "new": "（未振り分け）"}

raw = open("index.html", encoding="utf-8").read()
EVENTS = json.loads(re.search(r"  const EVENTS = (\[.*?\]);", raw, re.S).group(1))

rows = defaultdict(list)
for e in EVENTS:
    for t in e.get("tickets") or []:
        if t.get("soldout"):
            continue
        ty = t.get("type") or ""
        mm = re.search(r"%s\s*(\d{1,2}):(\d{2})\s*発売" % re.escape(MD), ty)
        if not (t.get("startDate") == TARGET or mm):
            continue
        hhmm = "%02d:%s" % (int(mm.group(1)), mm.group(2)) if mm else "??:??"
        genre = e.get("genre") if e.get("genre") != "new" else (e.get("_genre") or "new")
        kaiin = "会員限定" if ("会員限定" in ty or "poco" in ty) else ""
        rows[genre].append((hhmm, e.get("artist"), e.get("prefecture"), kaiin, ty))

order = sorted(rows, key=lambda g: -len(rows[g]))
for g in order:
    print("【%s】" % GN.get(g, g))
    seen = set()
    for hhmm, artist, pref, kaiin, ty in sorted(rows[g]):
        k = (artist, hhmm)
        if k in seen:
            continue
        seen.add(k)
        print("  %s %s／%s%s" % (hhmm, artist, pref, ("（%s）" % kaiin) if kaiin else ""))
    print("")
