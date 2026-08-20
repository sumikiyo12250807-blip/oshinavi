# -*- coding: utf-8 -*-
"""新着プール53件の振り分け案を出す（適用はしない）。
ルール: _genre をそのまま genre に移す。自分で再分類しない（project_vendor_genre_autoassign）。
人の判断が要るのは _piaSub が空 or「その他」の子だけ。"""
import io
import json
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

h = open(r"C:\Users\user\oshinavi\index.html", "rb").read().decode("utf-8")
evs = json.loads(re.search(r"  const EVENTS = (\[.*?\]);", h, re.S).group(1))
new = [e for e in evs if e.get("genre") == "new"]

# 2026-07-31 にユーザーが確定済みのもの
USER_FIXED = {3521: "jazz", 3523: "dento", 3525: "dento", 3550: "engeki"}
USER_EXTRA = {3550: ["kids"]}

auto, need = [], []
for e in new:
    g = e.get("_genre")
    sub = e.get("_piaSub") or ""
    if e["id"] in USER_FIXED:
        auto.append((e, USER_FIXED[e["id"]], USER_EXTRA.get(e["id"], e.get("_extraGenres") or []), "★ユーザー確定"))
    elif not sub or "その他" in sub or not g:
        need.append((e, g, sub))
    else:
        auto.append((e, g, e.get("_extraGenres") or [], sub))

by = {}
for e, g, ex, src in auto:
    by.setdefault(g, []).append((e, ex, src))

print("=== 振り分け案：自動適用できる %d件 ===" % len(auto))
for g in sorted(by, key=lambda x: -len(by[x])):
    print("\n--- %s (%d件) ---" % (g, len(by[g])))
    for e, ex, src in by[g]:
        tag = ("  +extra:%s" % ",".join(ex)) if ex else ""
        mark = "  " + src if src.startswith("★") else ""
        print("  id=%s %s%s%s" % (e["id"], (e.get("name") or "")[:46], tag, mark))

print("\n\n=== 🤔 人の判断が要る %d件（_piaSubが空 or その他）===" % len(need))
for e, g, sub in need:
    print("\n■ id=%s %s" % (e["id"], e.get("name")))
    print("   下書き_genre=%s / _piaSub=%r" % (g, sub))
    print("   %s / %s / 公演 %s" % (e.get("prefecture"), (e.get("venue") or "")[:50], e.get("date")))
    print("   pia: %s" % ((e.get("links") or {}).get("pia")))

print("\n合計 %d件（自動 %d ／ 要判断 %d）" % (len(new), len(auto), len(need)))
