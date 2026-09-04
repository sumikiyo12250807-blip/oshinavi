# -*- coding: utf-8 -*-
"""新着プールに全角ローマ字・全角数字が残っていないか点検する（半角化してからレビューする決まり）。"""
import json, re, io

OUT = "tmp/newpool_zenkaku_0905.txt"
ZEN = re.compile(r"[Ａ-Ｚａ-ｚ０-９]")

html = io.open("index.html", encoding="utf-8").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\s*\n", html, re.S).group(1))
news = sorted([e for e in events if e.get("genre") == "new"], key=lambda e: e["id"])

hits = []
for e in news:
    fields = {"name": e.get("name", ""), "artist": e.get("artist", ""),
              "venue": e.get("venue", ""), "dateLabel": e.get("dateLabel", "")}
    for i, t in enumerate(e.get("tickets", [])):
        fields["ticket[%d].type" % i] = t.get("type", "")
    bad = {k: v for k, v in fields.items() if ZEN.search(v or "")}
    if bad:
        hits.append((e["id"], e.get("name", ""), bad))

buf = ["全角ローマ字/数字が残っている新着エントリ: %d件 / 全%d件" % (len(hits), len(news)), ""]
for eid, name, bad in hits:
    buf.append("id=%s %s" % (eid, name))
    for k, v in bad.items():
        buf.append("    %s: %s" % (k, v))
io.open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("ZENKAKU_HITS=%d / %d" % (len(hits), len(news)))
