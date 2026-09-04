# -*- coding: utf-8 -*-
"""新着プール（genre=="new"）の一覧を UTF-8 で書き出す。振り分け作業用。"""
import json, re, io

OUT = "tmp/newpool_0905.txt"

html = io.open("index.html", encoding="utf-8").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\s*\n", html, re.S).group(1))

news = [e for e in events if e.get("genre") == "new"]
news.sort(key=lambda e: e["id"])

buf = ["新着プール %d件 (id %s 〜 %s)" % (len(news), news[0]["id"] if news else "-",
                                    news[-1]["id"] if news else "-"), ""]
srcs = {}
gcnt = {}
for e in news:
    links = e.get("links") or {}
    urls = [(k, v) for k, v in links.items() if v and k != "amazon"]
    for t in e.get("tickets", []):
        if t.get("url"):
            urls.append(("ticket", t["url"]))
    kinds = set(k for k, v in urls)
    src = "pia" if "pia" in kinds else ("eplus" if "eplus" in kinds else
          ("rakuten" if "rakuten" in kinds else ("lawson" if "lawson" in kinds else "none")))
    if src == "none":
        for k, v in urls:
            if "t.pia.jp" in v:
                src = "pia"
            elif "eplus.jp" in v:
                src = "eplus"
    srcs[src] = srcs.get(src, 0) + 1
    g = e.get("_genre") or "(なし)"
    gcnt[g] = gcnt.get(g, 0) + 1

    buf.append("id=%-5s [%s] %s | %s | %s | date=%s | _genre=%s | piaSub=%s | 枠%d"
               % (e["id"], src, e.get("name", ""), e.get("artist", ""), e.get("venue", ""),
                  e.get("date"), g, e.get("_piaSub", "-"), len(e.get("tickets", []))))
    for t in e.get("tickets", []):
        buf.append("        枠: %s | startDate=%s date=%s"
                   % (t.get("type"), t.get("startDate"), t.get("date")))
    for k, v in urls:
        buf.append("        %s: %s" % (k, v))

buf.append("")
buf.append("SOURCES: %s" % json.dumps(srcs, ensure_ascii=False))
buf.append("GENRES(_genre): %s" % json.dumps(gcnt, ensure_ascii=False))
io.open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("WROTE %s count=%d" % (OUT, len(news)))
print("SOURCES=%s" % json.dumps(srcs))
print("GENRES=%s" % json.dumps(gcnt, ensure_ascii=False).encode("ascii", "backslashreplace").decode())
