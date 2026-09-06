# -*- coding: utf-8 -*-
"""HEAD と現物を比べて、ticket.url が落ちた枠が無いかを全エントリで見る。
（feedback_build_pia_multiurl_loses_ticket_url＝url が落ちると翌朝から生きた枠を0枠と誤報する）
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")


def load(text):
    m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", text, re.S)
    return {e["id"]: e for e in json.loads(m.group(2))}


head = subprocess.run(["git", "show", "HEAD:index.html"], capture_output=True).stdout.decode("utf-8")
before = load(head)
after = load(open("index.html", encoding="utf-8").read())

lost = []
for eid, e in after.items():
    b = before.get(eid)
    if not b:
        continue
    nb = sum(1 for t in (b.get("tickets") or []) if t.get("url"))
    na = sum(1 for t in (e.get("tickets") or []) if t.get("url"))
    tb = len(b.get("tickets") or [])
    ta = len(e.get("tickets") or [])
    if na < nb:
        lost.append((eid, e.get("artist") or "", nb, na, tb, ta))

print("=== ticket.url が落ちたエントリ %d件 ===" % len(lost))
for eid, name, nb, na, tb, ta in lost:
    print("  id=%-5d %-38s url付き %d→%d枠 （枠数 %d→%d）" % (eid, name[:38], nb, na, tb, ta))
if not lost:
    print("  ✅ 1件も無い")
