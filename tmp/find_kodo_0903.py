# -*- coding: utf-8 -*-
"""9/3 20:00発売の鼓童×初音ミクを特定し、当日発売(startDate==2026-09-03)の枠を全部出す。"""
import json, re, io, sys

SRC = "index.html"
TODAY = "2026-09-03"

html = io.open(SRC, encoding="utf-8").read()
m = re.search(r"const EVENTS = (\[.*?\]);\s*\n", html, re.S)
if not m:
    print("EVENTS not found")
    sys.exit(1)
events = json.loads(m.group(1))
print("EVENTS:", len(events))

hits = []
for ev in events:
    for t in ev.get("tickets", []):
        if t.get("startDate") == TODAY:
            hits.append((ev, t))
            break

print("\n=== startDate==%s の枠を持つエントリ: %d件 ===" % (TODAY, len(hits)))
for ev, _ in hits:
    same = sum(1 for t in ev.get("tickets", []) if t.get("startDate") == TODAY)
    flat = sum(1 for t in ev.get("tickets", []) if t.get("startDate") == TODAY and t.get("startDate") == t.get("date"))
    print("id=%-6s %-46s 当日枠%d (うち締切未取込%d)" % (ev.get("id"), ev.get("name", "")[:44], same, flat))

print("\n=== 鼓童 ===")
for ev in events:
    if "鼓童" in ev.get("name", ""):
        print("id=%s  %s" % (ev.get("id"), ev.get("name")))
        for t in ev.get("tickets", []):
            print("    type=%s | startDate=%s | date=%s | url=%s"
                  % (t.get("type"), t.get("startDate"), t.get("date"), (t.get("url") or "")[:70]))
