# -*- coding: utf-8 -*-
"""9/5 当日発売なのに締切が入っていない枠（startDate==date==today）を全部出す。
type に発売時刻が入っているので、いちばん遅い発売が何時なのかもここで分かる。
出力は tmp/today_flat_0905.txt（UTF-8）。コンソールにはASCIIだけ出す。"""
import json, re, io

SRC = "index.html"
TODAY = "2026-09-05"
OUT = "tmp/today_flat_0905.txt"

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
buf = []
buf.append("締切未取込の当日枠: %d枠 / %d エントリ" % (len(rows), len(set(r[1] for r in rows))))
buf.append("")
for hhmm, eid, name, ttype, sold, url in rows:
    buf.append("%s  id=%-5s %s" % (hhmm, eid, name[:50]))
    buf.append("        %s%s" % (ttype[:90], "  [soldout]" if sold else ""))
    buf.append("        %s" % url[:110])
buf.append("")
buf.append("--- ids (heal用) ---")
buf.append(" ".join(str(i) for i in sorted(set(r[1] for r in rows))))
io.open(OUT, "w", encoding="utf-8").write("\n".join(buf))

# ASCIIだけコンソールへ
times = sorted(set(r[0] for r in rows if r[0] != "??:??"))
print("SLOTS=%d ENTRIES=%d" % (len(rows), len(set(r[1] for r in rows))))
print("TIMES=" + ",".join(times))
print("LATEST=" + (times[-1] if times else "NONE"))
print("UNKNOWN_TIME=%d" % sum(1 for r in rows if r[0] == "??:??"))
