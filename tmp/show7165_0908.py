# -*- coding: utf-8 -*-
import re, json, io
s = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", s, re.S).group(1))
e = [x for x in EV if x["id"] == 7165][0]
o = io.open("tmp/e7165.txt", "w", encoding="utf-8")
o.write(json.dumps({k: v for k, v in e.items() if k != "tickets"}, ensure_ascii=False, indent=1))
o.write("\n--- tickets ---\n")
for t in e["tickets"]:
    o.write(json.dumps(t, ensure_ascii=False) + "\n")
o.close()
print("wrote tmp/e7165.txt")
