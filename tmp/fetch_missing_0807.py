# -*- coding: utf-8 -*-
"""8/7 朝: reconcile で MISSING が出た6件のぴあ実枠を機械取得して JSON に落とす。"""
import io
import json
import subprocess
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TARGETS = [
    (187, "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2667137"),
    (513, "https://t.pia.jp/pia/event/event.do?eventCd=2619885"),
    (1026, "https://t.pia.jp/pia/event/event.do?eventCd=2623433"),
    (2243, "https://t.pia.jp/pia/event/event.do?eventCd=2622663"),
    (3475, "https://t.pia.jp/pia/event/event.do?eventCd=2612932"),
    (3513, "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669864"),
]

out = {}
for i, (eid, url) in enumerate(TARGETS):
    if i:
        time.sleep(6)
    r = subprocess.run(
        [sys.executable, "tools/pia_tickets.py", url, "--json", "--all"],
        capture_output=True,
    )
    txt = r.stdout.decode("utf-8", "replace")
    try:
        out[eid] = json.loads(txt)
        print("id=%d 取得 %d件" % (eid, len(out[eid])))
    except Exception as e:
        out[eid] = {"error": str(e), "raw": txt[:500]}
        print("id=%d 失敗: %s" % (eid, e))

with open("tmp/missing_0807.json", "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print("→ tmp/missing_0807.json")
