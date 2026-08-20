# -*- coding: utf-8 -*-
"""在庫の発売日分布を見る（なぜ補充が集まらないかの裏取り）。"""
import json, io, re, sys, datetime, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
TODAY = datetime.date(2026, 8, 6)


def days_until(r):
    m = re.match(r"(\d{4})/(\d{1,2})/(\d{1,2})", r or "")
    if not m:
        return None
    return (datetime.date(*[int(x) for x in m.groups()]) - TODAY).days


for tag in ["music", "engeki", "classic", "event", "sports", "art"]:
    rows = json.load(open("tmp/presale_%s03_0806.json" % tag, encoding="utf-8-sig"))["new"]
    c = collections.Counter()
    for r in rows:
        d = days_until(r.get("rlsdate"))
        c["不明" if d is None else ("4日以上" if d >= 4 else "%d日後" % d)] += 1
    print("%-8s 未掲載%3d件  %s" % (tag, len(rows), dict(c)))
