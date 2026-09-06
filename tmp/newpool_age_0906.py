# -*- coding: utf-8 -*-
"""いま新着タブに出ている100件が「いつ入ったもの」かを数える。
ユーザー「今日の新着100件って昨日と同じじゃない？」（2026-09-06 夜）の確認。
"""
import json
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))
pool = sorted([e for e in EVENTS if e.get("genre") == "new"], key=lambda e: e["id"])

# 投入バッチの記録から id範囲 → 投入日 を作る
bat = json.load(open(".claude/state/last_batch.json", encoding="utf-8"))["batches"]
def whenin(eid):
    for b in bat:
        if b.get("id_from") and b.get("id_to") and b["id_from"] <= eid <= b["id_to"]:
            return "%s %s" % (b["date"], b["slot"])
    return "記録なし"

def src(e):
    blob = json.dumps(e, ensure_ascii=False)
    if "t.pia.jp" in blob or "ticket.pia.jp" in blob:
        return "ぴあ"
    if "eplus.jp" in blob:
        return "e+"
    if "rakuten" in blob:
        return "楽天"
    return "その他"

cnt = collections.Counter()
for e in pool:
    cnt[(whenin(e["id"]), src(e))] += 1

print("いま新着タブに出ているのは %d件" % len(pool))
print("")
print("いつ投入したか / どこから / 件数")
for (w, s), n in sorted(cnt.items()):
    print("  %-22s %-4s %3d件" % (w, s, n))
print("")
print("id範囲 %d 〜 %d" % (pool[0]["id"], pool[-1]["id"]))
