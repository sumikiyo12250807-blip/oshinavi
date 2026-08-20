# -*- coding: utf-8 -*-
"""3475 キュウソネコカミの会場別 eventCd を個別に叩いて実枠を出す（8/7 朝）。"""
import io
import json
import subprocess
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

CODES = [
    ("岩手・宮城・秋田", "2612708"),
    ("新潟", "2627362"),
    ("石川", "2627363"),
    ("高知", "2627249"),
    ("静岡", "2628908"),
    ("北海道", "2612932"),
]

out = {}
for i, (label, cd) in enumerate(CODES):
    if i:
        time.sleep(6)
    url = "https://t.pia.jp/pia/event/event.do?eventCd=" + cd
    r = subprocess.run(
        [sys.executable, "tools/pia_tickets.py", url, "--json"],
        capture_output=True,
    )
    txt = r.stdout.decode("utf-8", "replace")
    try:
        rows = json.loads(txt)
    except Exception as e:
        out[label] = {"error": str(e), "raw": txt[:400]}
        print("%s 失敗" % label)
        continue
    out[label] = rows
    print("== %s (eventCd=%s) 買える枠 %d ==" % (label, cd, len(rows)))
    for r2 in rows:
        pr = r2["perfdate"] + ("〜" + r2["perf_end"] if r2.get("perf_end") and r2["perf_end"] != r2["perfdate"] else "")
        print("   [%s] %s %s %s | %s | %s" % (r2["state"], pr, r2["pref"], r2["venue"], r2["title"], r2["when"]))

with open("tmp/kyuso_0807.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
