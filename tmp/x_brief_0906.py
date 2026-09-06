# -*- coding: utf-8 -*-
"""Fableに渡す素材を組む。台本(X_SCRIPT.md)以外のルールは書かない。"""
import json
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

DAYS = [("2026-09-07", "9/7(月)"), ("2026-09-08", "9/8(火)"), ("2026-09-09", "9/9(水)")]

# 新着プール(振り分け前)は中身のジャンルで束に入れる
FORCE = {7037: "jpop", 7048: "engeki", 7057: "classic", 7076: "sports", 7092: "sonota"}

BUCKET = {
    "jpop": "音楽（JPOP・ロック）", "rock": "音楽（JPOP・ロック）",
    "idol": "音楽（JPOP・ロック）", "yougaku": "音楽（JPOP・ロック）",
    "vtuber": "音楽（JPOP・ロック）", "anime": "音楽（JPOP・ロック）",
    "seiyuu": "音楽（JPOP・ロック）",
    "classic": "クラシック", "jazz": "クラシック", "hougaku": "クラシック",
    "owarai": "落語・お笑い",
    "engeki": "舞台・ミュージカル", "musical": "舞台・ミュージカル", "dento": "舞台・ミュージカル",
    "sports": "スポーツ",
    "enka": "その他のイベント", "kids": "その他のイベント", "musicetc": "その他のイベント",
    "fanevent": "その他のイベント", "art": "その他のイベント", "hanabi": "その他のイベント",
    "sonota": "その他のイベント",
}

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))


def bucket(e):
    g = FORCE.get(e["id"]) or e.get("genre")
    return BUCKET.get(g, "その他のイベント")


def line(e, t):
    tt = t.get("type") or ""
    hm = re.search(r"(\d{1,2}):(\d{2})発売", tt)
    time = "%02d:%s" % (int(hm.group(1)), hm.group(2)) if hm else "??:??"
    senko = "（先行）" if ("先行" in tt or "プレリザーブ" in tt or "プリセール" in tt
                        or "オフィシャル先行" in tt) else ""
    return "%s %s／%s%s" % (time, e.get("artist") or "", e.get("prefecture") or "", senko)


data = {}
for day, label in DAYS:
    byb = collections.defaultdict(list)
    for e in EVENTS:
        for t in e.get("tickets") or []:
            if t.get("startDate") == day:
                byb[bucket(e)].append((e, t))
    data[day] = byb

BUCKETS = ["音楽（JPOP・ロック）", "クラシック", "落語・お笑い",
           "舞台・ミュージカル", "スポーツ", "その他のイベント"]

for b in BUCKETS:
    print("")
    print("=" * 70)
    print("■ まとめ投稿：%s" % b)
    print("=" * 70)
    for day, label in DAYS:
        rows = data[day].get(b) or []
        if not rows:
            continue
        if day == "2026-09-07":
            print("")
            print("【%s発売】← 明日ぶん。1件も削らずに全部並べる（%d件）" % (label, len(rows)))
            for e, t in rows:
                print("  " + line(e, t))
        else:
            print("")
            print("【%s発売】← 2〜3日後。この中から大物5件くらいに絞る（全%d件・会場のキャパで選ぶ）"
                  % (label, len(rows)))
            for e, t in rows:
                print("  %-46s ＠%s" % (line(e, t), (e.get("venue") or "")[:34]))
