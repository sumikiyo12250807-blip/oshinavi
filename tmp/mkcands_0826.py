# -*- coding: utf-8 -*-
"""新規候補を build_pia_entries の入力形式 [{newid, artist, urls}] に変換する。
idは既存の最大＋1から順に振る（欠番は詰めない＝feedback_candidate_list_stable_numbering）。"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

src = open("index.html", encoding="utf-8").read()
m = re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S)
events = json.loads(m.group(1))
nid = max(e["id"] for e in events) + 1
print("採番の開始id =", nid)

rows = json.load(open("tmp/cand_fresh_0826.json", encoding="utf-8"))
out = []
for r in rows:
    u = (r.get("url") or "").replace("ticket.pia.jp/pia/event.do", "t.pia.jp/pia/event/event.do")
    out.append({"newid": nid, "artist": r.get("artist"), "urls": [u]})
    nid += 1

json.dump(out, open("tmp/cands_0826.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("%d件 → tmp/cands_0826.json (id %d〜%d)" % (len(out), out[0]["newid"], out[-1]["newid"]))
