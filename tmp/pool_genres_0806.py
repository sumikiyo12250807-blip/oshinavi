# -*- coding: utf-8 -*-
"""新着プールの下書きジャンルを一覧する。ぴあカテゴリが取れていない子（人の判断が要る）を先頭に。"""
import json, re, io, sys, collections

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
src = open("index.html", "rb").read().decode("utf-8")
m = re.search(r"  const EVENTS = (\[.*?\]);", src, re.S)
data = json.loads(m.group(1))
pool = [e for e in data if e.get("genre") == "new"]

need = []
ok = []
for e in pool:
    sub = (e.get("_piaSub") or "").strip()
    if not sub or "その他" in sub:
        need.append(e)
    else:
        ok.append(e)

print("=== ぴあカテゴリが無い/その他＝人が見る %d件 ===" % len(need))
for e in need:
    print("  [%-8s] %-44s | %s | _piaSub=%s" % (
        e.get("_genre"), (e.get("artist") or "")[:44],
        (e.get("venue") or "")[:26], e.get("_piaSub") or "(空)"))

print("\n=== ぴあカテゴリ通りに適用 %d件 ===" % len(ok))
c = collections.Counter()
for e in ok:
    g = e.get("_genre")
    x = e.get("_extraGenres") or []
    c[g + ("+" + ",".join(x) if x else "")] += 1
for k, v in sorted(c.items(), key=lambda kv: -kv[1]):
    print("  %-18s %d件" % (k, v))
