# -*- coding: utf-8 -*-
"""「公演は終わっているのに生き枠がある」11件の中身を出す。
soldout / saleUntilSoldOut による見かけの生き枠か、本物の未来締切かを分ける。
"""
import re, json

TODAY = "2026-09-07"
IDS = [1904, 2300, 3120, 3229, 1613, 2035, 2341, 4971, 4980, 4982, 5239]

h = open("index.html", encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))
by = {e["id"]: e for e in EV}

with open("tmp/holdalive_0907.txt", "w", encoding="utf-8") as f:
    for eid in IDS:
        e = by.get(eid)
        if not e:
            f.write("id=%s 現物に無い\n" % eid)
            continue
        f.write("■ id=%s  公演%s  %s\n" % (eid, e.get("date"), e.get("name", "")[:52]))
        for t in e.get("tickets", []):
            sd, d = t.get("startDate"), t.get("date") or ""
            flags = []
            if t.get("soldout"):
                flags.append("soldout")
            if t.get("saleUntilSoldOut"):
                flags.append("saleUntilSoldOut")
            if t.get("saleEnded"):
                flags.append("saleEnded")
            past = (not sd or sd <= TODAY) and d < TODAY
            kind = "締切ずみ" if past else "🚨締切が未来(%s)" % d
            f.write("   - %-52s %s %s\n" % ((t.get("type") or "")[:52], kind, "/".join(flags) or "-"))
        f.write("\n")
print("wrote tmp/holdalive_0907.txt")
