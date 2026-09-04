# -*- coding: utf-8 -*-
"""新着プール93件のうち、既存エントリ（genre!="new"）と同名（正規化一致）のものを洗い出す。
統合候補＝ツアーが分裂している可能性。振り分ける前に見る。"""
import json, re, io, unicodedata

OUT = "tmp/samename_0905.txt"

html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・／/＜＞<>「」『』（）()【】’'\"!！\-—]", "", s).lower()


ex = {}
for e in events:
    if e.get("genre") == "new":
        continue
    for f in ("artist", "name"):
        v = e.get(f)
        if v:
            ex.setdefault(norm(v), []).append(e)

news = sorted([e for e in events if e.get("genre") == "new"], key=lambda e: e["id"])

buf = []
hit = 0
for e in news:
    keys = {norm(e.get(f)) for f in ("artist", "name") if e.get(f)}
    matched = []
    for k in keys:
        for o in ex.get(k, []):
            if o not in matched:
                matched.append(o)
    if not matched:
        continue
    hit += 1
    buf.append("新着 id=%-5s %s | %s | date=%s | 枠%d"
               % (e["id"], e.get("name", ""), e.get("venue", ""), e.get("date"), len(e.get("tickets", []))))
    for o in matched:
        buf.append("    既存 id=%-5s %s | %s | date=%s | genre=%s | 枠%d"
                   % (o["id"], o.get("name", ""), o.get("venue", ""), o.get("date"),
                      o.get("genre"), len(o.get("tickets", []))))
    buf.append("")

head = ["新着93件のうち既存と同名: %d件" % hit, ""]
io.open(OUT, "w", encoding="utf-8").write("\n".join(head + buf))
print("SAMENAME=%d / %d" % (hit, len(news)))
