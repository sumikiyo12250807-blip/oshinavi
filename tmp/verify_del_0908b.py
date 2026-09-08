# -*- coding: utf-8 -*-
"""補助チェック：削除候補と同名/類似のエントリが他idで残っているか"""
import json, io, os, re

TODAY = "2026-09-08"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "tmp", "verify_del_0908b.txt")

with io.open(os.path.join(ROOT, "index.html"), encoding="utf-8") as f:
    html = f.read()
start = html.index("const EVENTS = [")
bstart = html.index("[", start)
i, depth, in_str, quote, esc = bstart, 0, False, "", False
while i < len(html):
    c = html[i]
    if in_str:
        if esc: esc = False
        elif c == "\\": esc = True
        elif c == quote: in_str = False
    else:
        if c in "\"'": in_str, quote = True, c
        elif c == "[": depth += 1
        elif c == "]":
            depth -= 1
            if depth == 0: break
    i += 1
events = json.loads(html[bstart:i+1])

KEYS = ["ピクサー", "住吉踊り", "大須演芸場", "ヤミテラ", "透明少女", "黒蜜",
        "皇月結音", "HINONABE", "ちあきなおみ", "私はあなたを知らない",
        "凰稀かなめ", "永井千絵", "渡邊一丘", "CHAMPIONS SUMMIT", "一木万里奈"]
TARGET = {16, 271, 858, 1833, 2430, 2773, 3936, 5698, 5712, 6177, 6183, 6184, 6234, 6265, 6545}

lines = []
for k in KEYS:
    hits = []
    for e in events:
        blob = "%s %s %s" % (e.get("artist", ""), e.get("title", ""), e.get("venue", ""))
        if k in blob:
            hits.append(e)
    lines.append("### キーワード: %s  → %d件" % (k, len(hits)))
    for e in hits:
        mark = "[削除候補]" if e.get("id") in TARGET else "[残る]"
        lines.append("  %s id=%s date=%s %s / %s @%s"
                     % (mark, e.get("id"), e.get("date"), e.get("artist"), e.get("title"), e.get("venue")))
    lines.append("")

with io.open(OUT, "w", encoding="utf-8") as f:
    f.write("\n".join(lines) + "\n")
print("wrote", OUT)
