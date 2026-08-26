# -*- coding: utf-8 -*-
"""あたしの下書き(_genre)と、別エージェントがゼロから判定した結果を突き合わせる。
一致した分だけ振り分ける（feedback_new_pool_ok_before_assign＝割れた件はプールに残して報告）。"""
import json
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")

agent = {}
for line in open("tmp/agent_genres_0826.txt", encoding="utf-8"):
    parts = line.split()
    if len(parts) == 2:
        agent[int(parts[0])] = parts[1]

src = open("index.html", encoding="utf-8").read()
m = re.search(r"const EVENTS = (\[.*?\]);\n", src, re.S)
by_id = {e["id"]: e for e in json.loads(m.group(1))}

same, diff, maybe = [], [], []
for eid, g in sorted(agent.items()):
    e = by_id.get(eid)
    if not e:
        continue
    mine = e.get("_genre")
    if g == "迷い":
        maybe.append((eid, e.get("artist"), mine))
    elif g == mine:
        same.append((eid, e.get("artist"), g))
    else:
        diff.append((eid, e.get("artist"), mine, g, e.get("_piaSub")))

print("=== 突き合わせ %d件 ===" % len(agent))
print("  ✅一致（振り分ける）      %d件" % len(same))
print("  ⚠️割れた（プールに残す） %d件" % len(diff))
print("  🤔エージェントが迷い     %d件" % len(maybe))
print("")
print("=== ⚠️割れた分 ===")
for eid, artist, mine, g, sub in diff:
    print("  id=%-5d %-34s あたし=%-10s エージェント=%-10s （ぴあの区分: %s）" % (
        eid, (artist or "")[:34], mine, g, sub))
print("")
print("=== 🤔迷い ===")
for eid, artist, mine in maybe:
    print("  id=%-5d %-34s あたし=%s" % (eid, (artist or "")[:34], mine))

from collections import Counter
print("")
print("=== ✅一致分の内訳 ===")
for k, v in Counter(g for _, _, g in same).most_common():
    print("  %-12s %d" % (k, v))

json.dump([eid for eid, _, _ in same], open("tmp/assign_ok_0826.json", "w", encoding="utf-8"))
