# -*- coding: utf-8 -*-
"""統合の入力を作る前に、既存と候補の形（date/dateLabel/venue/prefecture）を見る。"""
import io, re, json

PAIRS = [(7207, 1202), (7327, 1202), (7284, 1273), (7285, 1273), (7286, 1273)]

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = {e["id"]: e for e in json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))}
cand = {e["id"]: e for e in json.load(io.open("tmp/inject_addto_0908.json", encoding="utf-8"))}

o = io.open("tmp/peek_merge_0908.txt", "w", encoding="utf-8")
seen = set()
for c_id, t_id in PAIRS:
    if t_id not in seen:
        e = EV[t_id]
        o.write("=== 既存 id%d ===\n" % t_id)
        for k in ("name", "date", "dateLabel", "venue", "prefecture"):
            o.write("  %-11s %s\n" % (k, e.get(k)))
        o.write("  tickets %d枠\n" % len(e.get("tickets") or []))
        for t in (e.get("tickets") or [])[:4]:
            o.write("     - %s | date=%s | url=%s\n"
                    % ((t.get("type") or "")[:44], t.get("date"), (t.get("url") or "")[:40]))
        seen.add(t_id)
    c = cand[c_id]
    o.write("--- 候補 id%d ---\n" % c_id)
    for k in ("name", "date", "dateLabel", "venue", "prefecture"):
        o.write("  %-11s %s\n" % (k, c.get(k)))
    for t in (c.get("tickets") or []):
        o.write("     + %s | date=%s | url=%s\n"
                % ((t.get("type") or "")[:44], t.get("date"), (t.get("url") or "")[:40]))
    o.write("\n")
o.close()
print("wrote tmp/peek_merge_0908.txt")
