# -*- coding: utf-8 -*-
"""9/5 削除候補（公演終了＋全販売終了）の詳細を UTF-8 で書き出す。"""
import json, re, io

IDS = [673, 917, 1209, 1242, 1613, 2215, 3114, 3408, 4471, 5030, 5579]
OUT = "tmp/del_cand_0905.txt"

html = io.open("index.html", encoding="utf-8").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\s*\n", html, re.S).group(1))
by = {e["id"]: e for e in events}

buf = []
for i in IDS:
    e = by.get(i)
    if not e:
        buf.append("MISSING id=%d" % i)
        continue
    urls = set()
    if e.get("url"):
        urls.add(e["url"])
    for t in e.get("tickets", []):
        if t.get("url"):
            urls.add(t["url"])
    buf.append("id=%s | %s | %s | date=%s | genre=%s | venue=%s"
               % (i, e.get("name"), e.get("title", ""), e.get("date"), e.get("genre"), e.get("venue", "")))
    for t in e.get("tickets", []):
        buf.append("    ticket: %s | startDate=%s date=%s soldout=%s saleEnded=%s url=%s"
                   % (t.get("type"), t.get("startDate"), t.get("date"),
                      t.get("soldout"), t.get("saleEnded"), t.get("url") or "-"))
    for u in sorted(urls):
        buf.append("    URL: %s" % u)
    buf.append("")

io.open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("WROTE %s entries=%d" % (OUT, len([i for i in IDS if i in by])))
