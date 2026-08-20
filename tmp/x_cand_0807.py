# -*- coding: utf-8 -*-
"""X投稿の候補＝指定日に「発売が始まる」枠を持つエントリを出す。

startDate が対象日の枠だけを見る（date は締切なので発売開始と混同しない
＝[[feedback_sale_start_vs_deadline]]）。
"""
import json, re, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TARGET = sys.argv[1] if len(sys.argv) > 1 else "2026-08-07"
src = open("index.html", "rb").read().decode("utf-8")
m = re.search(r"  const EVENTS = (\[.*?\]);", src, re.S)
data = json.loads(m.group(1))

rows = []
for e in data:
    hits = [t for t in (e.get("tickets") or []) if t.get("startDate") == TARGET]
    if not hits:
        continue
    rows.append((e, hits))

print("=== %s に発売開始する枠を持つエントリ %d件 ===" % (TARGET, len(rows)))
for e, hits in sorted(rows, key=lambda x: (x[0].get("genre") or "", x[0]["id"])):
    print("id%-5s [%-8s] %s" % (e["id"], e.get("genre") or e.get("_genre"), (e.get("artist") or "")[:46]))
    print("       %s / %s" % ((e.get("venue") or "")[:40], e.get("prefecture")))
    for t in hits:
        print("       ・%s" % t["type"][:70])
