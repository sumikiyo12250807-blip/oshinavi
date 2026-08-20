# -*- coding: utf-8 -*-
"""補充候補の材料を出す（music04 + engeki03/classic03 の残り）。"""
import json, io, re, sys, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
TODAY = datetime.date(2026, 8, 6)


def eventcd(u):
    m = re.search(r"event(?:Bundle)?Cd=(\w+)", u or "")
    return m.group(1) if m else ""


used = set()
for c in json.load(open("tmp/cand_new.json", encoding="utf-8-sig")):
    for u in c["urls"]:
        used.add(eventcd(u))

for f in ["tmp/presale_music04_0806.json", "tmp/presale_engeki03_0806.json",
          "tmp/presale_classic03_0806.json"]:
    rows = json.load(open(f, encoding="utf-8-sig"))["new"]
    print("=== %s" % f.split("/")[-1])
    for r in rows:
        if eventcd(r["url"]) in used:
            continue
        print("  %-10s | %-40s | %-26s | %s | %s" % (
            r.get("rlsdate") or "不明", r["artist"][:40], (r.get("perfdate") or "")[:26],
            (r.get("pref") or "")[:8], r["url"]))
