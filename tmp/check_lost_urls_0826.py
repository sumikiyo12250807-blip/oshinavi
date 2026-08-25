# -*- coding: utf-8 -*-
"""救済(heal --apply)の前後で ticket.url が落ちていないかを点検する。

なぜ必要か（feedback_build_pia_multiurl_loses_ticket_url）:
  build_pia_entries に複数URLを渡すと2本目以降の枠に ticket.url が付かない。
  ticket.url は reconcile_pia が「どのぴあページを見るか」の入力でもあるので、
  落ちると翌朝から会場別ページを見なくなり、生きた枠が見えなくなる（4044 堂島孝平で実害）。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

IDS = set(int(x) for x in sys.argv[1].split(","))
BEFORE = sys.argv[2]
AFTER = sys.argv[3]


def load(path):
    src = open(path, encoding="utf-8").read()
    m = re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S)
    return {e["id"]: e for e in json.loads(m.group(1))}


b = load(BEFORE)
a = load(AFTER)

print("=== 救済前後で ticket.url が消えたぴあURL ===")
hit = 0
for i in sorted(IDS):
    eb, ea = b.get(i), a.get(i)
    if not eb or not ea:
        continue
    ub = set(t.get("url") for t in (eb.get("tickets") or []) if (t.get("url") or "").find("t.pia.jp") >= 0)
    ua = set(t.get("url") for t in (ea.get("tickets") or []) if (t.get("url") or "").find("t.pia.jp") >= 0)
    lost = ub - ua
    lost = set(u for u in lost if u != (ea.get("links") or {}).get("pia"))
    if lost:
        hit += 1
        print("id=%-5d %s" % (i, (ea.get("artist") or "")[:30]))
        print("      links.pia = %s" % ((ea.get("links") or {}).get("pia")))
        for u in sorted(lost):
            print("      消えたurl = %s" % u)
print("")
print("該当 %d件 / 点検 %d件" % (hit, len(IDS)))
