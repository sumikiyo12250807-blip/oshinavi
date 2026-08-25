# -*- coding: utf-8 -*-
"""新着プール(genre:new)の一覧を出す。振り分け前の下ごしらえ用。"""
import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

src = open("index.html", encoding="utf-8").read()
m = re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S)
events = json.loads(m.group(1))

pool = [e for e in events if e.get("genre") == "new"]
print("新着プール %d件" % len(pool))
ids = [e["id"] for e in pool]
print("id範囲: %d〜%d" % (min(ids), max(ids)))

from collections import Counter
print("\n_piaSub の内訳:")
for k, v in Counter(e.get("_piaSub") or "(なし)" for e in pool).most_common():
    print("  %-24s %d" % (k, v))
print("\n_genre(下書き)の内訳:")
for k, v in Counter(e.get("_genre") or "(なし)" for e in pool).most_common():
    print("  %-24s %d" % (k, v))

print("\n=== 一覧 ===")
for e in sorted(pool, key=lambda x: x["id"]):
    links = e.get("links") or {}
    vendor = ",".join(k for k in ("pia", "rakuten", "lawson", "eplus") if links.get(k))
    print("id=%-5d %-10s %-12s 公演%s 枠%d %s @ %s [%s]" % (
        e["id"], e.get("_genre") or "-", e.get("_piaSub") or "-", e.get("date"),
        len(e.get("tickets") or []), (e.get("artist") or "")[:34], (e.get("venue") or "")[:20], vendor))
