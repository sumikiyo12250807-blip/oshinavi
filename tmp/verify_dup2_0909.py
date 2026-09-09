# -*- coding: utf-8 -*-
"""【M/D（曜）HH:MM公演】のような「時間別枠」が今日足されたのに、
   同じ日の「総称枠」が残っていないか（＝同じ公演が二重に見える）を洗う。"""
import json
import re
import io
import sys
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
NEW = r"C:\Users\user\oshinavi\index.html"
OLD = r"C:\Users\user\oshinavi\index.html.bak_0909_prenoonheal"


def load_events(path):
    lines = io.open(path, "r", encoding="utf-8").read().split("\n")
    s = next(i for i, ln in enumerate(lines) if ln.strip() == "const EVENTS = [")
    e = next(j for j in range(s + 1, len(lines)) if lines[j].rstrip("\r") == "];")
    body = "\n".join(lines[s:e + 1]).replace("const EVENTS = [", "[", 1).rstrip()
    return {x["id"]: x for x in json.loads(body[:-1])}


new, old = load_events(NEW), load_events(OLD)
BR = re.compile(r"【.*?】")          # 【】の中に（）が入っても消す
TAIL = re.compile(r"（[^（）]*?公演）")
TIMEBR = re.compile(r"【[^】]*\d{1,2}:\d{2}[^】]*公演[^】]*】")

buf = []
buf.append("===== 時間別枠と総称枠の並存（同じ url / startDate / date）=====")
hits = 0
for i, e in new.items():
    oldtys = set(t.get("type") for t in old.get(i, {}).get("tickets", []))
    groups = defaultdict(list)
    for t in e.get("tickets", []):
        ty = t.get("type") or ""
        m = list(TAIL.finditer(ty))
        if not m:
            continue
        day = m[-1].group(0)
        head = BR.sub("", ty[:m[-1].start()]).strip()
        groups[(head, day, t.get("url"), t.get("startDate"), t.get("date"))].append(ty)
    for k, v in groups.items():
        has_time = [x for x in v if TIMEBR.search(x)]
        generic = [x for x in v if not BR.search(x)]
        if has_time and generic:
            newly = [x for x in v if x not in oldtys]
            if not newly:
                continue
            hits += 1
            buf.append("  id=%s %s / %s" % (i, e.get("artist"), e.get("name")))
            buf.append("      url=%s start=%s end=%s" % (k[2], k[3], k[4]))
            for x in v:
                buf.append("        %s %s" % ("[今日追加]" if x in newly else "[前からある]", x))
buf.append("該当グループ数=%d" % hits)
io.open(r"C:\Users\user\oshinavi\tmp\verify_dup2_0909.txt", "w", encoding="utf-8").write("\n".join(buf) + "\n")
print("ok hits=%d" % hits)
