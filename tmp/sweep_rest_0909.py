# -*- coding: utf-8 -*-
"""総ざらいの残り（主役4組以外）を build_pia_entries に渡す候補JSONにする。

🚨ここで作るのは「候補」だけ。統合するか新エントリにするかは、
   組み立てた中身（会場・公演日）を見てから決める。
   ・同じ公演の券種違い → 既存へ統合
   ・別の日・別の公演    → 新エントリ（新着プールへ）
   🚨スポーツの主催違い（ホーム/ビジター）は絶対に畳まない
     （feedback_sports_home_away_never_merge）
"""
import io, json, re, sys

sys.stdout.reconfigure(encoding="utf-8")

DONE = ["モーニング娘。", "矢野顕子", "宇都宮隆", "二見颯一"]

st = json.load(io.open("tmp/sweep_x_0909_state.json", encoding="utf-8"))
res = st["results"]

cands, rows = [], []
nid = 91000
for kw in sorted(res):
    if kw in DONE:
        continue
    for m in res[kw]["missing"]:
        if not m["own_name"]:
            continue
        nid += 1
        cands.append({"newid": nid, "artist": kw, "urls": [m["url"]]})
        rows.append("%d\t%s\t%s\t%s\t%s\t%s"
                    % (nid, kw, m["status"], m["perfdate"], m["venue"], m["title"]))

io.open("tmp/sweep_rest_0909.json", "w", encoding="utf-8").write(
    json.dumps(cands, ensure_ascii=False, indent=1))
io.open("tmp/sweep_rest_0909.tsv", "w", encoding="utf-8").write("\n".join(rows) + "\n")
print("候補 %d件 -> tmp/sweep_rest_0909.json" % len(cands))
by = {}
for c in cands:
    by[c["artist"]] = by.get(c["artist"], 0) + 1
for k in sorted(by, key=lambda x: -by[x]):
    print("  %-24s %d件" % (k, by[k]))
