# -*- coding: utf-8 -*-
"""新規候補に newid を振る。
🚨削除済みidを再利用しない＝現存の最大idだけでなく、last_batch.json の id_to も見る
（過去に消したidを使い回すと、後から見た時にログと突き合わせられなくなる）。"""
import io, json, re, sys
sys.stdout.reconfigure(encoding="utf-8")

src = io.open("index.html", encoding="utf-8").read()
evs = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S).group(1))
mx = max(e["id"] for e in evs)
lb = json.load(io.open(".claude/state/last_batch.json", encoding="utf-8"))
mx = max([mx] + [b.get("id_to") or 0 for b in lb["batches"]])
start = mx + 1
print("現存とlast_batchの最大id=%d → %d から振る" % (mx, start))

cands = json.load(io.open("tmp/new_cand_0909.json", encoding="utf-8"))
for n, c in enumerate(cands):
    c["newid"] = start + n
json.dump(cands, io.open("tmp/new_cand_0909.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("%d件に id %d..%d を振った" % (len(cands), start, start + len(cands) - 1))
