# -*- coding: utf-8 -*-
"""9/3 当日発売なのに締切が入っていない枠（startDate==date==today）を全部出す。
type に発売時刻が入っているので、いちばん遅い発売が何時なのかもここで分かる。"""
import json, re, io, sys

SRC = "index.html"
TODAY = "2026-09-03"

html = io.open(SRC, encoding="utf-8").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\s*\n", html, re.S).group(1))

rows = []
for ev in events:
    for t in ev.get("tickets", []):
        if t.get("startDate") == TODAY and t.get("date") == TODAY:
            m = re.search(r"(\d{1,2}):(\d{2})\s*発売", t.get("type", ""))
            hhmm = "%02d:%s" % (int(m.group(1)), m.group(2)) if m else "??:??"
            rows.append((hhmm, ev.get("id"), ev.get("name", ""), t.get("type", ""),
                         bool(t.get("soldout")), (t.get("url") or "")))

rows.sort()
print("締切未取込の当日枠: %d枠 / %d エントリ" % (len(rows), len(set(r[1] for r in rows))))
print()
for hhmm, eid, name, ttype, sold, url in rows:
    print("%s  id=%-5s %s" % (hhmm, eid, name[:40]))
    print("        %s%s" % (ttype[:90], "  [soldout]" if sold else ""))
    print("        %s" % url[:100])
print()
print("--- ids (heal用) ---")
print(" ".join(str(i) for i in sorted(set(r[1] for r in rows))))
