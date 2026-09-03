# -*- coding: utf-8 -*-
"""9/3から持ち越した二重登録4件（3370/3735/3752/5516）の枠を全部出す。
url有り/無しで同じ枠が二重になっているかを機械で確かめる。"""
import json, re, io

IDS = [3370, 3735, 3752, 5516]
html = io.open("index.html", encoding="utf-8").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\s*\n", html, re.S).group(1))
by_id = {e.get("id"): e for e in events}

buf = []
for i in IDS:
    e = by_id.get(i)
    if not e:
        buf.append("id=%s 見つからない" % i)
        continue
    buf.append("=" * 70)
    buf.append("id=%s  %s  / %s" % (i, e.get("name"), e.get("title", "")))
    buf.append("  公演日=%s  genre=%s  url=%s" % (e.get("date"), e.get("genre"), e.get("url")))
    ts = e.get("tickets", [])
    buf.append("  枠数=%d" % len(ts))
    for n, t in enumerate(ts):
        buf.append("   [%02d] type=%s" % (n, t.get("type")))
        buf.append("        startDate=%s date=%s soldout=%s" % (t.get("startDate"), t.get("date"), t.get("soldout")))
        buf.append("        url=%s" % (t.get("url") or "(なし)"))
    # type別に url有り/無しの重複を数える
    from collections import defaultdict
    g = defaultdict(lambda: {"withurl": 0, "nourl": 0})
    for t in ts:
        k = (t.get("type"), t.get("date"))
        if t.get("url"):
            g[k]["withurl"] += 1
        else:
            g[k]["nourl"] += 1
    dups = [(k, v) for k, v in g.items() if v["withurl"] and v["nourl"]]
    buf.append("  -> url有り/無しで二重になっている枠: %d種" % len(dups))
    for k, v in dups:
        buf.append("     %s (%s)  url有%d / url無%d" % (k[0], k[1], v["withurl"], v["nourl"]))

io.open("tmp/dup_check_0904.txt", "w", encoding="utf-8").write("\n".join(buf))
print("WROTE tmp/dup_check_0904.txt")
for i in IDS:
    e = by_id.get(i)
    print("id=%s slots=%s" % (i, len(e.get("tickets", [])) if e else "NOTFOUND"))
