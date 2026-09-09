# -*- coding: utf-8 -*-
"""改行コードの壊れ(CRCRLF/LF混在)と、今日足された枠の内訳を見る。"""
import json
import io
import sys
from collections import Counter

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
NEW = r"C:\Users\user\oshinavi\index.html"
OLD = r"C:\Users\user\oshinavi\index.html.bak_0909_prenoonheal"
TODAY = "2026-09-09"

for p in (NEW, OLD):
    b = open(p, "rb").read()
    crlf = b.count(b"\r\n")
    cr = b.count(b"\r")
    lf = b.count(b"\n")
    print("%s : CRLF=%d 単独CR=%d 単独LF=%d CRCRLF=%d" % (
        p.split("\\")[-1], crlf, cr - crlf, lf - crlf, b.count(b"\r\r\n")))


def load_events(path):
    lines = io.open(path, "r", encoding="utf-8").read().split("\n")
    s = next(i for i, ln in enumerate(lines) if ln.strip() == "const EVENTS = [")
    e = next(j for j in range(s + 1, len(lines)) if lines[j].rstrip("\r") == "];")
    body = "\n".join(lines[s:e + 1]).replace("const EVENTS = [", "[", 1).rstrip()
    return {x["id"]: x for x in json.loads(body[:-1])}


new, old = load_events(NEW), load_events(OLD)
c = Counter()
past = []
for i, e in new.items():
    oldtys = Counter(t.get("type") for t in old.get(i, {}).get("tickets", []))
    seen = Counter()
    for t in e.get("tickets", []):
        ty = t.get("type")
        seen[ty] += 1
        if seen[ty] > oldtys.get(ty, 0):
            sd, d = t.get("startDate"), t.get("date")
            if t.get("soldout"):
                c["売切/販売終了"] += 1
            elif sd and sd > TODAY:
                c["発売前"] += 1
            elif d and d < TODAY:
                c["すでに締切(画面に出ない)"] += 1
                past.append((i, e.get("artist"), ty, sd, d))
            else:
                c["販売中"] += 1
print("\n今日足された枠(type完全一致ベース)の内訳: %s  合計=%d" % (dict(c), sum(c.values())))
for r in past[:20]:
    print("  過去日: id=%s %s %s start=%s end=%s" % r)
