# -*- coding: utf-8 -*-
"""振り分け対象のリストを作る。エージェントには**下書きジャンルを見せない**
（feedback_verify_independent_not_anchored＝候補値にアンカーさせない）。"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

EXCLUDE = set(
    # 昨日からユーザーに聞いたまま返事待ちの保留分
    [5098, 5119, 5120, 5122, 5127, 5131, 5132, 5139, 5156, 5191, 5197]
    # 今日投入＝明日チェックする分
    + [5301, 5303, 5304, 5306, 5307, 5308, 5318, 5319, 5320, 5321, 5322,
       5325, 5326, 5327, 5328, 5330, 5331]
    # ぴあが「〜その他」に入れた＝人が決める分
    + [5205, 5209, 5235, 5236, 5237, 5268, 5276, 5286]
    # 下書きが怪しい（映画/邦画 → engeki になっている）
    + [5240]
)

src = open("index.html", encoding="utf-8").read()
m = re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S)
pool = [e for e in json.loads(m.group(1)) if e.get("genre") == "new"]
target = [e for e in pool if e["id"] not in EXCLUDE]

print("新着プール %d件 / 除外 %d件 / 振り分け対象 %d件" % (len(pool), len(pool) - len(target), len(target)))
print("")
for e in sorted(target, key=lambda x: x["id"]):
    print("id=%d | %s | 会場: %s | %s | 公演%s" % (
        e["id"], e.get("artist"), e.get("venue"), e.get("prefecture"), e.get("date")))

json.dump([e["id"] for e in target], open("tmp/assign_ids_0826.json", "w", encoding="utf-8"))
