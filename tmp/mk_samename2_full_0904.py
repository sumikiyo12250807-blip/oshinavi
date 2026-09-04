# -*- coding: utf-8 -*-
"""統合候補を確定させる。
   自動統合44件 ＋ 要確認5件のうち4件（同じ公演・同じシリーズと確認できたもの）＝48件。

🚨「日本フィル 第九特別演奏会2026（阪哲朗指揮）」は統合しない＝オーケストラは「1公演＝1エントリ」が
   多数派で、id1837 だけが例外的に31枠を抱えている（[[project_pia_presale_caught_up]]）。
   → 新規投入に回す（今朝の6462と同じ扱い）。
"""
import json, io, re
from collections import defaultdict

ADD = {
    "2635005": 4279,   # 市川團十郎特別公演≪3階左右列見切れ席≫ → 市川團十郎特別公演
    "2635341": 1711,   # 桂吉弥独演会 Vol.24 → 桂吉弥独演会
    "2632313": 1131,   # 春風亭小朝 独演会 ～初春は春風とともに～ → 春風亭小朝独演会
    "2632836": 309,    # しまじろうコンサート ～...～ → しまじろうコンサート
}
NEW_ENTRY = {"2634652"}   # 日本フィル 第九特別演奏会2026（阪哲朗指揮）＝新規投入へ

cand = json.load(io.open("tmp/samename2_cand_0904.json", encoding="utf-8"))
tri = json.load(io.open("tmp/_triage_0904.json", encoding="utf-8"))["samename"]
by_url = {}
for it in tri:
    m = re.search(r"event(?:Bundle)?Cd=(\w+)", it.get("url") or "")
    if m:
        by_url[m.group(1)] = it

seq = defaultdict(int)
for c in cand:
    seq[c["_merge_into"]] += 1

for cd, into in ADD.items():
    it = by_url.get(cd)
    if not it:
        print("NOT FOUND %s" % cd); continue
    seq[into] += 1
    cand.append({"newid": 920000 + into * 10 + seq[into], "artist": it.get("artist", ""),
                 "urls": [it["url"]], "_merge_into": into})

json.dump(cand, io.open("tmp/samename2_cand_0904.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

newc = []
for n, cd in enumerate(sorted(NEW_ENTRY), 1):
    it = by_url.get(cd)
    if it:
        newc.append({"newid": 6700 + n, "artist": it.get("artist", ""), "urls": [it["url"]]})
json.dump(newc, io.open("tmp/newentry_cand_0904.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("MERGE_CAND=%d (統合先 %dエントリ)" % (cand.__len__(), len(set(c["_merge_into"] for c in cand))))
print("NEW_ENTRY_CAND=%d" % len(newc))
