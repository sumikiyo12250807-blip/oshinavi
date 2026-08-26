# -*- coding: utf-8 -*-
"""今日のスイープで見つかった「同名の既存あり」93件を、既存エントリ単位の統合planにする。
（tmp/cand_samename_0826.json → tmp/merge_todo2_0826.json）"""
import json
import re
import sys
import unicodedata
from collections import defaultdict

sys.stdout.reconfigure(encoding="utf-8")


def norm(s):
    s = unicodedata.normalize("NFKC", s or "")
    return re.sub(r"[\s　・/／'’\"”!！?？\-–—~〜＜＞<>【】「」『』（）()]", "", s).lower()


src = open("index.html", encoding="utf-8").read()
m = re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S)
events = json.loads(m.group(1))
by_norm = defaultdict(list)
for e in events:
    by_norm[norm(e.get("artist"))].append(e)

rows = json.load(open("tmp/cand_samename_0826.json", encoding="utf-8"))
plan = defaultdict(list)
skipped = []
for r in rows:
    hits = by_norm.get(norm(r.get("artist")))
    if not hits:
        skipped.append(r)
        continue
    # 新着プール(genre:new)は並び順が動くと困るので統合先にしない＝正式ジャンルのものを優先
    cand = [e for e in hits if e.get("genre") != "new"] or hits
    tgt = sorted(cand, key=lambda e: e.get("date") or "")[-1]
    plan[tgt["id"]].append(r.get("url"))

json.dump({str(k): v for k, v in plan.items()},
          open("tmp/merge_todo2_0826.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("統合対象 %d エントリ（元 %d件 / 対応が取れず %d件）→ tmp/merge_todo2_0826.json"
      % (len(plan), len(rows), len(skipped)))
newpool = [i for i in plan if next(e for e in events if e["id"] == i).get("genre") == "new"]
print("うち新着プールのエントリ %d件（最早dateが動くなら適用されない）" % len(newpool))
