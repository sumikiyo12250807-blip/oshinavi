# -*- coding: utf-8 -*-
"""新着プールの _piaSub → _genre の対応を点検する。
要注意型（海外ROCK・POPS／伝統／その他）だけを別立てで出す。"""
import json, re, io

OUT = "tmp/newpool_genre_check_0905.txt"

html = io.open("index.html", encoding="utf-8").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\s*\n", html, re.S).group(1))
news = sorted([e for e in events if e.get("genre") == "new"], key=lambda e: e["id"])

pair = {}
for e in news:
    key = (e.get("_piaSub", "-"), e.get("_genre") or "(なし)")
    pair.setdefault(key, []).append(e["id"])

buf = ["=== _piaSub → _genre の対応（新着%d件） ===" % len(news), ""]
for (sub, g), ids in sorted(pair.items()):
    buf.append("%-28s -> %-10s %2d件  ids=%s" % (sub, g, len(ids), " ".join(str(i) for i in ids)))

WATCH = ["海外", "伝統", "その他", "クラシック/", "邦楽"]
buf.append("")
buf.append("=== 要注意（海外/伝統/その他）の実物 ===")
for e in news:
    sub = e.get("_piaSub", "") or ""
    if any(w in sub for w in WATCH):
        buf.append("id=%-5s %s | %s | piaSub=%s | _genre=%s"
                   % (e["id"], e.get("name", ""), e.get("artist", ""), sub, e.get("_genre")))
        links = e.get("links") or {}
        if links.get("pia"):
            buf.append("        %s" % links["pia"])

io.open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("WROTE %s pairs=%d" % (OUT, len(pair)))
