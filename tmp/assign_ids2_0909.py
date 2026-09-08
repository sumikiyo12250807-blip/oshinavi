# -*- coding: utf-8 -*-
"""候補ファイルに newid を振る（削除済みidを再利用しない）。
使い方: python tmp/assign_ids2_0909.py <cand.json> [追加で避けるid,...]"""
import io, json, re, sys
sys.stdout.reconfigure(encoding="utf-8")
SRC = sys.argv[1]
skip = {int(x) for x in sys.argv[2].split(',')} if len(sys.argv) > 2 else set()

h = io.open("index.html", encoding="utf-8").read()
evs = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))
mx = max(e["id"] for e in evs)
lb = json.load(io.open(".claude/state/last_batch.json", encoding="utf-8"))
mx = max([mx] + [b.get("id_to") or 0 for b in lb["batches"]] + list(skip))
start = mx + 1
cands = json.load(io.open(SRC, encoding="utf-8"))
for n, c in enumerate(cands):
    c["newid"] = start + n
json.dump(cands, io.open(SRC, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("最大id=%d → %d件に id %d..%d を振った" % (mx, len(cands), start, start + len(cands) - 1))
