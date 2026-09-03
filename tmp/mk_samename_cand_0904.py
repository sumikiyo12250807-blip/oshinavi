# -*- coding: utf-8 -*-
"""統合対象90件の build 用候補JSONを作る。
🚨1エントリ＝1URL（複数URLを渡すと2本目以降の ticket.url が落ちる
   ＝[[feedback_build_pia_multiurl_loses_ticket_url]]）。
newid は「統合先の既存id × 連番」の仮番号。後で既存エントリへ枠を足すときの目印にする。"""
import json, io
from collections import defaultdict

rows = [l.split("\t") for l in io.open("tmp/samename_urls_0904.tsv", encoding="utf-8").read().split("\n") if l.strip()]
cand = json.load(io.open("tmp/_triage_0903.json", encoding="utf-8"))["samename"]
by_url = {c.get("url"): c for c in cand}

seq = defaultdict(int)
out = []
for eid, url in rows:
    seq[eid] += 1
    it = by_url.get(url) or {}
    out.append({
        "newid": 900000 + int(eid) * 10 + seq[eid],   # 仮番号（既存id×10＋連番）
        "artist": it.get("artist", ""),
        "urls": [url],
        "_merge_into": int(eid),
    })

json.dump(out, io.open("tmp/samename_cand_0904.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("CAND=%d  entries=%d" % (len(out), len(set(r[0] for r in rows))))
print("WROTE tmp/samename_cand_0904.json")
