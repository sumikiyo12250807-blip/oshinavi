# -*- coding: utf-8 -*-
"""新着50件のうち QC未照合(skip)になりうる枠＝同じ締切表記が複数ある枠を洗い出す。
reconcile は「同締切の枠が複数で対を確定できない」時に照合を飛ばすので、そこは人が見る。
"""
import collections
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

evs = json.load(open(r"C:\Users\user\oshinavi\tmp\built_0807.json", encoding="utf-8"))
SUF = re.compile(r"(〜\d{1,2}/\d{1,2}[^）]*|\d{1,2}/\d{1,2} \d{1,2}:\d{2}発売)$")

n = 0
for e in evs:
    tks = e.get("tickets") or []
    if len(tks) < 2:
        continue
    c = collections.Counter()
    for t in tks:
        m = SUF.search(t.get("type") or "")
        c[m.group(1) if m else "(SUFなし)"] += 1
    dups = {k: v for k, v in c.items() if v > 1}
    if dups:
        n += 1
        print("id%-5d %s（%s %s）" % (e["id"], (e.get("artist") or "")[:40],
                                     e.get("prefecture", ""), e.get("date", "")))
        for t in tks:
            m = SUF.search(t.get("type") or "")
            k = m.group(1) if m else "(SUFなし)"
            mark = "  ←同締切" if dups.get(k) else ""
            print("     %s%s" % (t.get("type"), mark))
        print("     pia: %s" % ((e.get("links") or {}).get("pia") or ""))
print("=== 同締切が重なるエントリ %d件 ===" % n)
