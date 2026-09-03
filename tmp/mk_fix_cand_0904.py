# -*- coding: utf-8 -*-
"""照合で取りこぼしが出た 6410 / 6412 を build し直すための候補JSONを作る。
🚨1エントリ＝1URLで渡す（複数URLだと2本目以降のticket.urlが落ちる）。"""
import json, re, io

IDS = [6410, 6412]
html = io.open("index.html", encoding="utf-8", newline="").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", html, re.S).group(1))
by_id = {e.get("id"): e for e in events}

out = []
for i in IDS:
    e = by_id[i]
    urls = []
    p = (e.get("links") or {}).get("pia")
    if p:
        urls.append(p)
    for t in e.get("tickets", []):
        u = t.get("url")
        if u and "pia" in u and u not in urls:
            urls.append(u)
    print("id=%s urls=%d" % (i, len(urls)))
    for u in urls:
        print("   %s" % u)
    out.append({"newid": i, "artist": e.get("artist", ""), "urls": urls[:1]})

json.dump(out, io.open("tmp/fix_cand_0904.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("WROTE tmp/fix_cand_0904.json")
