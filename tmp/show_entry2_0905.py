# -*- coding: utf-8 -*-
"""指定 id のエントリを人が読める形で書き出す（出力先を引数で指定できる版）。
使い方: python tmp/show_entry2_0905.py <出力先.txt> <id> <id> ...
🚨 URLは index.html から機械抽出したものだけを出す（手で書かない＝DELETE_GATE 4.7）。
"""
import re, json, io, sys

OUT = sys.argv[1]
h = open("index.html", encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))
by = {e["id"]: e for e in EV}

buf = []
for a in sys.argv[2:]:
    e = by.get(int(a))
    if not e:
        buf.append("id=%s は現物に無い" % a)
        continue
    buf.append("■ id=%s  %s" % (e["id"], e.get("name", "")))
    buf.append("   genre=%s  venue=%s / %s  公演日=%s"
               % (e.get("genre"), e.get("venue"), e.get("prefecture"), e.get("date")))
    L = {k: v for k, v in (e.get("links") or {}).items() if v and k != "amazon"}
    buf.append("   links: " + (" / ".join("%s=%s" % (k, v) for k, v in L.items()) or "(なし)"))
    for t in e.get("tickets") or []:
        flags = []
        if t.get("soldout"):
            flags.append("soldout")
        if t.get("saleEnded"):
            flags.append("saleEnded")
        if t.get("saleUntilSoldOut"):
            flags.append("saleUntilSoldOut")
        if t.get("saleEndUnknown"):
            flags.append("saleEndUnknown")
        buf.append("   - %s  [%s]" % (t.get("type"), ",".join(flags) or "-"))
        buf.append("     締切=%s 開始=%s url=%s" % (t.get("date"), t.get("startDate"), t.get("url") or "(なし)"))
    buf.append("")

io.open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("wrote %s (%d lines)" % (OUT, len(buf)))
