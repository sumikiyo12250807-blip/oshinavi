# -*- coding: utf-8 -*-
"""1日にどれだけ新着を入れられたかの実績を数える。

🚨「今日は76件だったから1日70件」でペースを見積もったのが誤り（2026-09-07 ユーザー指摘
   「できるだけ入れるって言った日は200件以上載せれたのに」）。
   **平均でなく、本気で入れた日の実績**を分母にする。
"""
import io, json, collections

st = json.load(io.open(".claude/state/last_batch.json", encoding="utf-8"))

day = collections.OrderedDict()
for b in st["batches"]:
    d = b.get("date")
    if not d:
        continue
    a = day.setdefault(d, {"n": 0, "batches": []})
    a["n"] += b.get("count", 0)
    a["batches"].append("%s %d件" % (b.get("slot", "?"), b.get("count", 0)))

with io.open("tmp/pace_0907.txt", "w", encoding="utf-8") as f:
    f.write("=== 日ごとの新着投入数（last_batch.json の記録）===\n\n")
    for d in sorted(day):
        a = day[d]
        f.write("%s  %4d件   （%s）\n" % (d, a["n"], " / ".join(a["batches"])))
    ns = [day[d]["n"] for d in day]
    ns_sorted = sorted(ns, reverse=True)
    f.write("\n記録のある日数 %d日 / 合計 %d件\n" % (len(ns), sum(ns)))
    f.write("いちばん多い日 %d件 ／ 上位5日 %s\n" % (max(ns), ns_sorted[:5]))
    f.write("平均 %.1f件/日 ／ 中央値 %.1f件/日\n"
            % (sum(ns) / len(ns), sorted(ns)[len(ns) // 2]))
print("記録 %d日 / 最多 %d件 / 上位5日 %s" % (len(ns), max(ns), ns_sorted[:5]))
