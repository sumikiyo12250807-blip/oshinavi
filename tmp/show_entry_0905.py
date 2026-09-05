# -*- coding: utf-8 -*-
"""index.html の EVENTS から指定 id のエントリを人が読める形で書き出す。
使い方: python tmp/show_entry_0905.py 3050 6053  → tmp/show_entry_0905.txt
"""
import re, json, io, sys

h = open("index.html", encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))
by = {e["id"]: e for e in EV}

buf = []
for a in sys.argv[1:]:
    e = by.get(int(a))
    if not e:
        buf.append("id=%s は現物に無い" % a)
        continue
    buf.append("■ id=%s  %s" % (e["id"], e.get("name", "")))
    buf.append("   artist=%s  genre=%s  extraGenres=%s" % (e.get("artist"), e.get("genre"), e.get("extraGenres")))
    buf.append("   venue=%s / %s   date=%s  dateLabel=%s" % (e.get("venue"), e.get("prefecture"), e.get("date"), e.get("dateLabel")))
    buf.append("   links=%s" % json.dumps(e.get("links") or {}, ensure_ascii=False))
    for t in e.get("tickets") or []:
        buf.append("   - type=%s" % t.get("type"))
        buf.append("     date=%s startDate=%s soldout=%s url=%s"
                   % (t.get("date"), t.get("startDate"), t.get("soldout"), t.get("url") or "(なし)"))
    buf.append("")

io.open("tmp/show_entry_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("wrote tmp/show_entry_0905.txt (%d lines)" % len(buf))
