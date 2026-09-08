# -*- coding: utf-8 -*-
"""新エントリ候補58件に本番idを振り、投入用JSONにする。
   idは既存の最大＋1から連番（feedback_new_list_order_lock＝並びは投入順で固定）。"""
import io, json, re, sys

sys.stdout.reconfigure(encoding="utf-8")

新 = json.load(io.open("tmp/sweep_new_0909.json", encoding="utf-8"))
s = io.open("index.html", encoding="utf-8", newline="").read()
evs = json.loads(re.search(r"(  const EVENTS = )(\[.*?\])(;)", s, re.S).group(2))
mx = max(e["id"] for e in evs)

old2new = {}
for i, e in enumerate(新):
    old2new[e["id"]] = mx + 1 + i
    e["id"] = mx + 1 + i
    # 下書きジャンルは _genre に入っている。genre は "new" のまま（振り分けは朝）
    assert e.get("genre") == "new", e["id"]

io.open("tmp/sweep_inject_0909.json", "w", encoding="utf-8").write(
    json.dumps(新, ensure_ascii=False, indent=1))
io.open("tmp/sweep_idmap_0909.json", "w", encoding="utf-8").write(
    json.dumps(old2new, ensure_ascii=False, indent=1))
print("採番 %d件 id%d..%d" % (len(新), mx + 1, mx + len(新)))

g = {}
for e in 新:
    k = e.get("_genre") or "(下書き無し)"
    g[k] = g.get(k, 0) + 1
for k in sorted(g, key=lambda x: -g[x]):
    print("  %-12s %d件" % (k, g[k]))

# 発売前 / もう売っている の内訳（feedback_newpool_presale_ratio_gate）
pre = sum(1 for e in 新 if any(t.get("startDate") for t in e.get("tickets") or []))
print("発売前をふくむ %d件 / もう買える枠だけ %d件" % (pre, len(新) - pre))
