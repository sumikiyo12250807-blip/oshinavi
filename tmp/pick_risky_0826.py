# -*- coding: utf-8 -*-
"""新着プールから「間違いが起きやすい子」を選ぶ。
＝複数枠を持つ／全国ツアー（＝複数会場でバンドルの取りこぼしが起きる）／bundleURL。
別エージェントにゼロから再導出させる対象に使う。"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

LO, HI = (int(x) for x in sys.argv[1].split("-"))

src = open("index.html", encoding="utf-8").read()
m = re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S)
events = [e for e in json.loads(m.group(1)) if e.get("genre") == "new"]
events = [e for e in events if LO <= e["id"] <= HI]

risky = []
for e in events:
    ts = e.get("tickets") or []
    pia = (e.get("links") or {}).get("pia") or ""
    reason = []
    if len(ts) >= 2:
        reason.append("枠%d" % len(ts))
    if "ツアー" in (e.get("venue") or "") or "／" in (e.get("venue") or ""):
        reason.append("複数会場")
    if "Bundle" in pia:
        reason.append("bundle")
    if reason:
        risky.append((e, reason))

print("対象 %d件 / うち要注意 %d件" % (len(events), len(risky)))
for e, reason in risky:
    print("")
    print("id=%d | %s" % (e["id"], e.get("artist")))
    print("   会場: %s / %s" % (e.get("venue"), e.get("prefecture")))
    print("   公演日(登録): %s   理由: %s" % (e.get("date"), ",".join(reason)))
    print("   URL: %s" % ((e.get("links") or {}).get("pia")))
