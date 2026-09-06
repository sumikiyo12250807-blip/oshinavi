# -*- coding: utf-8 -*-
"""9/7・9/8・9/9 発売の枠をジャンル別に出す（X投稿の素材）。
台本＝明日のぶんはそのジャンル全部／2〜3日後は5件くらい（大物＝箱の大きさで選ぶ）。
"""
import json
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

DAYS = [("2026-09-07", "9/7(月)"), ("2026-09-08", "9/8(火)"), ("2026-09-09", "9/9(水)")]

# ジャンルを投稿の束にまとめる
BUCKET = {
    "jpop": "音楽（JPOP・ロック）", "rock": "音楽（JPOP・ロック）",
    "idol": "音楽（JPOP・ロック）", "yougaku": "音楽（JPOP・ロック）",
    "enka": "演歌・歌謡", "hougaku": "演歌・歌謡", "chanson": "演歌・歌謡",
    "classic": "クラシック", "jazz": "クラシック",
    "owarai": "落語・お笑い",
    "engeki": "舞台・ミュージカル", "musical": "舞台・ミュージカル", "dento": "舞台・ミュージカル",
    "sports": "スポーツ",
    "kids": "こども向け",
    "new": "✨新着（振り分け前）",
}

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

for day, label in DAYS:
    rows = []
    for e in EVENTS:
        for t in e.get("tickets") or []:
            if t.get("startDate") == day:
                rows.append((e, t))
    byb = collections.defaultdict(list)
    for e, t in rows:
        byb[BUCKET.get(e.get("genre"), "その他")].append((e, t))
    print("")
    print("################ %s 発売  合計%d本 ################" % (label, len(rows)))
    for b in sorted(byb, key=lambda x: -len(byb[x])):
        print("")
        print("=== %s : %d本 ===" % (b, len(byb[b])))
        for e, t in byb[b]:
            tt = t.get("type") or ""
            hm = re.search(r"(\d{1,2}):(\d{2})発売", tt)
            time = "%02d:%s" % (int(hm.group(1)), hm.group(2)) if hm else "??:??"
            senko = "（先行）" if ("先行" in tt or "プレリザーブ" in tt or "プリセール" in tt) else ""
            print("  %s %s／%s%s  [id%s %s 公演%s]" % (
                time, (e.get("artist") or "")[:32], e.get("prefecture") or "-", senko,
                e["id"], (e.get("venue") or "")[:24], e.get("date")))
            print("        券種: %s" % tt)
