# -*- coding: utf-8 -*-
"""9/6のスイープ結果の件数と、発売前／もう売ってる の比率を出す（feedback_newpool_presale_ratio_gate）。"""
import json
import os
import sys
import datetime

sys.stdout.reconfigure(encoding="utf-8")

TODAY = datetime.date(2026, 9, 6)
NAMES = {"01": "音楽", "02": "演劇", "03": "スポーツ", "04": "映画",
         "05": "アート", "06": "イベント", "07": "クラシック"}

total = 0
allrows = []
for code in ("01", "02", "07", "03", "04", "05", "06"):
    p = "tmp/presale_%s_0906.json" % code
    if not os.path.exists(p):
        print("  %s %s : ファイル無し" % (code, NAMES[code]))
        continue
    d = json.load(open(p, encoding="utf-8"))
    rows = d["new"]
    total += len(rows)
    for r in rows:
        r["_lg"] = code
    allrows += rows
    print("  lg=%s %-6s : 未掲載 %3d件  （ぴあ全%d件・パース%d件・同名の既存あり%d件）"
          % (code, NAMES[code], len(rows), d.get("total", 0), d.get("parsed", 0),
             d.get("new_name_in_db", 0)))

print("")
print("合計 %d件" % total)

# 発売日で「これから発売」かどうかを数える
pre, today_, unknown, past = 0, 0, 0, 0
for r in allrows:
    d = (r.get("rlsdate") or "").strip()
    if not d:
        unknown += 1
    elif d == "TODAY":
        today_ += 1
    else:
        try:
            y, mo, dd = [int(x) for x in d.split("/")]
            dt = datetime.date(y, mo, dd)
            if dt > TODAY:
                pre += 1
            elif dt == TODAY:
                today_ += 1
            else:
                past += 1
        except Exception:
            unknown += 1

print("発売前(明日以降) %d / 本日発売 %d / 発売日が過去 %d / 発売日不明 %d"
      % (pre, today_, past, unknown))

json.dump(allrows, open("tmp/presale_all_0906.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("→ tmp/presale_all_0906.json")
