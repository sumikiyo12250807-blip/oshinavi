# -*- coding: utf-8 -*-
"""URL単位で枠が減った5エントリの中身を前後で並べて見る。"""
import json
import io
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
NEW = r"C:\Users\user\oshinavi\index.html"
OLD = r"C:\Users\user\oshinavi\index.html.bak_0909_prenoonheal"
IDS = [571, 950, 1772, 4103, 5573]


def load_events(path):
    lines = io.open(path, "r", encoding="utf-8").read().split("\n")
    s = next(i for i, ln in enumerate(lines) if ln.strip() == "const EVENTS = [")
    e = next(j for j in range(s + 1, len(lines)) if lines[j].rstrip("\r") == "];")
    body = "\n".join(lines[s:e + 1]).replace("const EVENTS = [", "[", 1).rstrip()
    return {x["id"]: x for x in json.loads(body[:-1])}


new, old = load_events(NEW), load_events(OLD)
buf = []
for i in IDS:
    for tag, src in (("旧", old), ("新", new)):
        e = src[i]
        buf.append("=== id=%s [%s] %s / %s (枠%d)" % (i, tag, e.get("artist"), e.get("name"), len(e.get("tickets", []))))
        for t in e.get("tickets", []):
            buf.append("    type=%s" % t.get("type"))
            buf.append("      start=%s end=%s soldout=%s url=%s" % (
                t.get("startDate"), t.get("date"), t.get("soldout"), t.get("url")))
    buf.append("")
io.open(r"C:\Users\user\oshinavi\tmp\verify_urls_0909.txt", "w", encoding="utf-8").write("\n".join(buf) + "\n")
print("ok")
