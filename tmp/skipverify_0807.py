# -*- coding: utf-8 -*-
"""QC未照合(skip)の4枠を、ぴあ実ページの券種と目で突き合わせられる形に出す。
  3915 務川慧悟（福岡12/6）＝一般発売と子供舞台芸術鑑賞体験支援事業が同じ締切
  3925 Mozu ミニチュア展（石川9/4〜10/4）＝一般発売とグッズ付が同じ締切
"""
import io
import json
import subprocess
import sys
import time

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

TARGETS = [
    (3915, "務川慧悟（p）福岡12/6", "https://t.pia.jp/pia/event/event.do?eventCd=2626041"),
    (3925, "Mozu ミニチュア展（bundle）", "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670032"),
]

for i, (eid, label, url) in enumerate(TARGETS):
    if i:
        time.sleep(6)
    r = subprocess.run([sys.executable, "tools/pia_tickets.py", url, "--json"], capture_output=True)
    txt = r.stdout.decode("utf-8", "replace")
    print("=" * 74)
    print("id=%d %s" % (eid, label))
    try:
        rows = json.loads(txt)
    except Exception as e:
        print("  解析失敗 %s\n%s" % (e, txt[:300]))
        continue
    for x in rows:
        pr = x["perfdate"] + ("〜" + x["perf_end"] if x.get("perf_end") and x["perf_end"] != x["perfdate"] else "")
        print("  [%s] %s %s %s | %s | %s" % (x["state"], pr, x["pref"], x["venue"], x["title"], x["when"]))
