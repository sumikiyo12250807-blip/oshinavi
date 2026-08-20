# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
base = r"C:\Users\user\oshinavi"
built = json.load(open(base + r"\tmp\final_built.json", encoding="utf-8"))
html = open(base + r"\index.html", encoding="utf-8").read()

parts = []
for o in built:
    s = json.dumps(o, ensure_ascii=False, indent=2)
    s = "\n".join("  " + ln for ln in s.split("\n"))
    parts.append(s)
block = ",\n".join(parts)

anchor = "\n  }\n];;;;;;;;"
assert html.count(anchor) == 1, "anchor count=" + str(html.count(anchor))
html = html.replace(anchor, "\n  },\n" + block + "\n];;;;;;;;")

ids = [o["id"] for o in built]
neworder = "const NEW_ORDER = [" + ",".join(map(str, ids)) + "];"
assert html.count("const NEW_ORDER = [];") == 1, "NEW_ORDER marker missing"
html = html.replace("const NEW_ORDER = [];", neworder)

open(base + r"\index.html", "w", encoding="utf-8").write(html)
print("inserted", len(built), "entries; NEW_ORDER", ids[0], "-", ids[-1])
