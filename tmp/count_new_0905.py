# -*- coding: utf-8 -*-
"""新着プール(genre:"new")の件数と、今日投入した分の内訳を数える。"""
import re, json, io

h = open("index.html", encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))
NO = re.search(r"NEW_ORDER = \[([^\]]*)\]", h)
order = [int(x) for x in re.findall(r"\d+", NO.group(1))] if NO else []

new = [e for e in EV if e.get("genre") == "new"]
slots = sum(len(e.get("tickets") or []) for e in new)

# 今日投入した範囲（別セッションとの取り決め）
RANGES = [
    ("朝の便・ぴあ発売前(音楽)", 6904, 6934),
    ("e+（別セッション・第1便）", 6935, 6945),
    ("ぴあ『ユイカ』『清春』", 6946, 6947),
    ("e+（別セッション・第2便）", 6948, 6986),
    ("ぴあ発売前(演劇・クラシック)", 6987, 7024),
]

buf = ["新着プール（genre:\"new\"）= %d件 / %d枠   NEW_ORDER = %d件" % (len(new), slots, len(order)), ""]
tot = 0
for label, a, b in RANGES:
    xs = [e for e in new if a <= int(e["id"]) <= b]
    s = sum(len(e.get("tickets") or []) for e in xs)
    tot += len(xs)
    buf.append("  %-30s %3d件 / %3d枠   (id %d〜%d)" % (label, len(xs), s, a, b))
buf.append("")
rest = [e for e in new if not any(a <= int(e["id"]) <= b for _, a, b in RANGES)]
buf.append("  それ以前から残っている分            %3d件" % len(rest))
if rest:
    buf.append("    " + ", ".join(str(e["id"]) for e in sorted(rest, key=lambda x: int(x["id"]))[:40]))
buf.append("")
buf.append("今日投入した合計 = %d件" % tot)

io.open("tmp/count_new_0905.txt", "w", encoding="utf-8").write("\n".join(buf))
print("NEWPOOL=%d SLOTS=%d TODAY=%d" % (len(new), slots, tot))
