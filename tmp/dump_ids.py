# -*- coding: utf-8 -*-
import json, io, sys, re
SRC = r"C:\Users\user\oshinavi\index.html"
OUT = r"C:\Users\user\oshinavi\tmp\dump_ids_out.txt"
TARGET = [1006, 1904, 1487, 2866, 68]

def load_events(path):
    s = io.open(path, "r", encoding="utf-8").read()
    key = "const EVENTS = ["
    i = s.index(key); start = i + len(key) - 1
    depth = 0; in_str = False; esc = False; end = None
    for j in range(start, len(s)):
        c = s[j]
        if in_str:
            if esc: esc = False
            elif c == "\\": esc = True
            elif c == '"': in_str = False
            continue
        if c == '"': in_str = True
        elif c in "[{": depth += 1
        elif c in "]}":
            depth -= 1
            if depth == 0: end = j; break
    return json.loads(s[start:end+1])

ev = load_events(SRC)
L = []
for e in ev:
    if e.get("id") in TARGET:
        L.append(json.dumps(e, ensure_ascii=False, indent=1))
        L.append("")
io.open(OUT, "w", encoding="utf-8").write("\n".join(L))
print("ok", len(L))
