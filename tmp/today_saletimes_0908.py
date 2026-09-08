# -*- coding: utf-8 -*-
"""今日(2026-09-08)発売の枠の発売時刻を全部出す。昼ヒールの実行時刻を決めるため。"""
import json, re, io, sys, collections

TODAY = "2026-09-08"

src = open("index.html", encoding="utf-8").read()
m = re.search(r"const EVENTS\s*=\s*(\[.*?\]);\s*\n", src, re.S)
if not m:
    print("EVENTS not found"); sys.exit(1)
events = json.loads(m.group(1))

times = collections.Counter()
rows = []
for e in events:
    for t in e.get("tickets", []) or []:
        sd = t.get("startDate")
        if sd != TODAY:
            continue
        ty = t.get("type", "") or ""
        mm = re.search(r"(\d{1,2}):(\d{2})", ty)
        hhmm = "%02d:%s" % (int(mm.group(1)), mm.group(2)) if mm else "??:??"
        times[hhmm] += 1
        rows.append((hhmm, e.get("id"), e.get("artist", "")[:24]))

out = io.open("tmp/today_saletimes_0908.txt", "w", encoding="utf-8")
out.write("today=%s  startDate==today の枠 %d件\n\n" % (TODAY, len(rows)))
for hhmm, n in sorted(times.items()):
    out.write("%s  %d件\n" % (hhmm, n))
out.write("\n--- 明細 ---\n")
for r in sorted(rows):
    out.write("%s  id%s  %s\n" % r)
out.close()
print("wrote tmp/today_saletimes_0908.txt  rows=%d  slots=%s" % (len(rows), sorted(times.items())))
