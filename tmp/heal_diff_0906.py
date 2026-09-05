# -*- coding: utf-8 -*-
"""ヒール適用の前後で「画面に出る枠(visible)」の数をエントリごとに突合する。
DELETE_GATE.md 5.＝ヒールの安全弁は公演単位でしか比べないので、
同じ公演の券種違いを丸ごと潰しても気づかない（2026-09-01 阪神×広島 12枠→1枠）。
"""
import json
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

TODAY = "2026-09-06"


def visible(t):
    if t.get("saleUntilSoldOut") or t.get("soldout"):
        return True
    sd, d = t.get("startDate"), t.get("date")
    return not ((not sd or sd <= TODAY) and (d or "") < TODAY)


def load(text):
    m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", text, re.S)
    return {e["id"]: e for e in json.loads(m.group(2))}


head = subprocess.run(["git", "show", "HEAD:index.html"],
                      capture_output=True).stdout.decode("utf-8")
before = load(head)
after = load(open("index.html", encoding="utf-8").read())

lost = []
gained = []
for eid, e in after.items():
    b = before.get(eid)
    if not b:
        continue
    nb = sum(1 for t in (b.get("tickets") or []) if visible(t))
    na = sum(1 for t in (e.get("tickets") or []) if visible(t))
    if na < nb:
        lost.append((eid, e.get("artist") or e.get("title") or "", nb, na))
    elif na > nb:
        gained.append((eid, e.get("artist") or e.get("title") or "", nb, na))

print("=== 画面に出る枠が減ったエントリ %d件 ===" % len(lost))
for eid, name, nb, na in sorted(lost, key=lambda x: x[2] - x[3], reverse=True):
    print("  id=%-5d %-38s %d枠 → %d枠  (-%d)" % (eid, name[:38], nb, na, nb - na))
print("")
print("=== 増えたエントリ %d件（発売時刻後に締切が入った分） ===" % len(gained))
for eid, name, nb, na in sorted(gained, key=lambda x: x[3] - x[2], reverse=True)[:20]:
    print("  id=%-5d %-38s %d枠 → %d枠  (+%d)" % (eid, name[:38], nb, na, na - nb))
print("")
print("エントリ数 before=%d after=%d" % (len(before), len(after)))
