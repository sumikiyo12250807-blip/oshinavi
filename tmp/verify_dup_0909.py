# -*- coding: utf-8 -*-
"""今日の書き換えで生まれた枠の重複を探す。
 (a) 同一エントリ内で type が完全に同じ枠
 (b) 「総称枠」と「時間別枠」が同じ公演日で並んでいる（同じ公演が2重3重に見える）
"""
import json
import re
import io
import sys
from collections import Counter, defaultdict

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
buf = []

# (a) 完全同一 type
buf.append("===== (a) 同一エントリ内で type が完全に同じ枠 =====")
na = ob = 0
rows = []
for i, e in new.items():
    c = Counter(t.get("type") for t in e.get("tickets", []))
    d = {k: v for k, v in c.items() if v > 1}
    if d:
        oc = Counter(t.get("type") for t in old.get(i, {}).get("tickets", []))
        od = {k: v for k, v in oc.items() if v > 1}
        rows.append((i, e, d, od))
        na += 1
        if od:
            ob += 1
buf.append("新で重複ありのエントリ=%d (うち旧でも重複=%d → 今日できた重複=%d)" % (na, ob, na - ob))
for i, e, d, od in rows[:30]:
    buf.append("  id=%s %s / %s  新=%s 旧=%s" % (i, e.get("artist"), e.get("name"), d, od))

# (b) 総称枠 + 時間別枠
buf.append("")
buf.append("===== (b) 同じ公演日で「総称」と「時間別【】」が並んでいる =====")
PAREN = re.compile(r"（([^（）]*?公演)）")
BR = re.compile(r"【[^】]*】")
hits = []
for i, e in new.items():
    groups = defaultdict(list)
    for t in e.get("tickets", []):
        ty = t.get("type") or ""
        m = PAREN.search(ty)
        if not m:
            continue
        head = BR.sub("", ty.split("（")[0]).strip()
        groups[(head, m.group(1), t.get("startDate"), t.get("date"))].append(ty)
    for k, v in groups.items():
        if len(v) > 1 and any("【" in x for x in v) and any("【" not in x for x in v):
            oldtys = [x.get("type") for x in old.get(i, {}).get("tickets", [])]
            newly = [x for x in v if x not in oldtys]
            hits.append((i, e, k, v, newly))
buf.append("該当エントリ数=%d" % len(set(h[0] for h in hits)))
for i, e, k, v, newly in hits[:40]:
    buf.append("  id=%s %s / %s" % (i, e.get("artist"), e.get("name")))
    buf.append("      キー=%s" % (k,))
    for x in v:
        buf.append("        %s %s" % ("[今日追加]" if x in newly else "[前からある]", x))

io.open(r"C:\Users\user\oshinavi\tmp\verify_dup_0909.txt", "w", encoding="utf-8").write("\n".join(buf) + "\n")
print("ok %d lines" % len(buf))
