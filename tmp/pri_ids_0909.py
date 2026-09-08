# -*- coding: utf-8 -*-
"""総ざらいで出た主役4組について、既存エントリのidと今持っている枠を出す。
   足す前に「今どうなっているか」を見るため（feedback_check_duplicates）。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

s = io.open("index.html", encoding="utf-8", newline="").read()
m = re.search(r"const EVENTS = (\[.*?\]);\r?\n", s, re.S)
evs = json.loads(m.group(1))

NAMES = ["モーニング娘", "矢野顕子", "宇都宮隆", "二見颯一"]
for nm in NAMES:
    print("=" * 60)
    print("■", nm)
    for e in evs:
        blob = (e.get("title") or "") + (e.get("artist") or "")
        if nm not in blob:
            continue
        print("  id%-5s %s" % (e["id"], e.get("title")))
        print("    ジャンル=%s 公演日=%s 会場=%s 県=%s"
              % (e.get("genre"), e.get("date"), e.get("venue"), e.get("prefecture")))
        print("    pia=%s" % (e.get("links", {}) or {}).get("pia"))
        for t in e.get("tickets", []) or []:
            print("      - %s | %s | %s" % (t.get("type"), t.get("date"), t.get("url")))
