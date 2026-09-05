# -*- coding: utf-8 -*-
"""9/6スイープの未掲載候補78件を build_pia_entries 用の候補JSONにする。
- 発売日不明は入れない（推測で日付を入れない＝feedback_no_placeholder_dates）
- 同名の既存エントリがある候補は別ファイルに分けて、統合を検討する材料にする
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

rows = json.load(open("tmp/presale_all_0906.json", encoding="utf-8"))

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
maxid = max(e["id"] for e in EVENTS)
print("既存エントリ %d件 / 最大id %d" % (len(EVENTS), maxid))

# URL単位で重複を潰す（ぴあの一覧は1公演1行＝同じeventCdが複数行に出る）
seen = {}
for r in rows:
    u = r["url"]
    if u not in seen:
        seen[u] = r
uniq = list(seen.values())
print("URL重複を潰して %d件 → %d件" % (len(rows), len(uniq)))

nodate = [r for r in uniq if not (r.get("rlsdate") or "").strip()]
have = [r for r in uniq if (r.get("rlsdate") or "").strip()]
print("発売日不明で見送り %d件 / 候補 %d件" % (len(nodate), len(have)))
for r in nodate:
    print("   見送り: %s  %s" % (r.get("artist"), r["url"]))

samename = [r for r in have if r.get("name_in_db")]
fresh = [r for r in have if not r.get("name_in_db")]
print("同名の既存あり %d件（統合を検討）/ 完全新規 %d件" % (len(samename), len(fresh)))

nid = maxid + 1
cand = []
for r in have:
    cand.append({"newid": nid, "artist": r["artist"], "urls": [r["url"]],
                 "_samename": bool(r.get("name_in_db")), "_lg": r.get("_lg")})
    nid += 1

json.dump(cand, open("tmp/cand_0906.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
json.dump(samename, open("tmp/samename_0906.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("→ tmp/cand_0906.json (%d件) / tmp/samename_0906.json (%d件)" % (len(cand), len(samename)))
print("id範囲 %d 〜 %d" % (maxid + 1, nid - 1))
