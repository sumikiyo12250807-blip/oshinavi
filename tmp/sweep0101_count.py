# -*- coding: utf-8 -*-
"""スイープ結果の候補を数えて重複を潰す。投入前ゲート用の数字を出す。"""
import io, json, glob, os, collections

GJP = {"01": "音楽", "02": "演劇", "03": "スポーツ", "04": "映画",
       "05": "アート", "06": "イベント", "07": "クラシック"}

rows = []
per_file = []
for p in sorted(glob.glob("tmp/sweep0101_0908/*.json")):
    try:
        d = json.load(io.open(p, encoding="utf-8"))
    except Exception as ex:
        per_file.append((os.path.basename(p), -1, str(ex)[:40])); continue
    cands = d if isinstance(d, list) else (d.get("candidates") or d.get("new") or [])
    per_file.append((os.path.basename(p), len(cands), ""))
    base = os.path.basename(p).replace(".json", "")
    tag, lg = base.rsplit("_", 1)
    for c in cands:
        c["_src"] = tag
        c["_lg"] = lg
        rows.append(c)

# eventCd で重複を潰す（同じ公演が発売前・抽選の両方に出ることがある）
def key(c):
    for k in ("eventCd", "eventcd", "cd", "url"):
        if c.get(k):
            return str(c[k])
    return json.dumps(c, sort_keys=True, ensure_ascii=False)[:120]

uniq = {}
for c in rows:
    uniq.setdefault(key(c), c)

o = io.open("tmp/sweep0101_count.md", "w", encoding="utf-8")
W = o.write
W("# 9/8 発売前スイープの棚卸し\n\n")
W("| ファイル | 未掲載候補 |\n|---|---|\n")
for name, n, err in per_file:
    W("| %s | %s |\n" % (name, n if n >= 0 else "読めず:" + err))
W("\n- 候補の延べ数＝**%d件**\n- eventCdで重複を潰すと＝**%d件**\n\n" % (len(rows), len(uniq)))

byg = collections.Counter(GJP.get(c["_lg"], c["_lg"]) for c in uniq.values())
W("## ジャンル別（重複を潰したあと）\n\n| ジャンル | 件数 |\n|---|---|\n")
for g, n in byg.most_common():
    W("| %s | %d |\n" % (g, n))

# 候補1件の中身を見せる（キー名を確かめるため）
if uniq:
    W("\n## 候補1件の中身（キー名の確認用）\n\n```\n%s\n```\n"
      % json.dumps(list(uniq.values())[0], ensure_ascii=False, indent=1))
o.close()
json.dump(list(uniq.values()), io.open("tmp/sweep0101_cand.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("total=%d uniq=%d -> tmp/sweep0101_count.md / tmp/sweep0101_cand.json"
      % (len(rows), len(uniq)))
