# -*- coding: utf-8 -*-
"""data-event-json の中身を取り出して、公演と販売枠が入っているか確かめる。"""
import io, re, sys, json, html

sys.stdout.reconfigure(encoding="utf-8")
h = io.open("tmp/rk_raw.html", encoding="utf-8").read()

m = re.search(r"data-event-json=(\"|')(.*?)\1", h, re.S)
if not m:
    print("data-event-json が見つからない")
    sys.exit(1)

raw = html.unescape(m.group(2))
io.open("tmp/rk_event.json", "w", encoding="utf-8").write(raw)
print("生の長さ: %d" % len(raw))

try:
    d = json.loads(raw)
except Exception as ex:
    print("JSONとして読めない: %s" % ex)
    print(raw[:400])
    sys.exit(1)


def walk(o, depth=0, path=""):
    pad = "  " * depth
    if isinstance(o, dict):
        for k, v in list(o.items())[:40]:
            if isinstance(v, (dict, list)):
                n = len(v)
                print("%s%s: %s(%d)" % (pad, k, type(v).__name__, n))
                if depth < 2:
                    walk(v, depth + 1, path + "/" + k)
            else:
                s = str(v)
                print("%s%s = %s" % (pad, k, s[:70]))
    elif isinstance(o, list):
        for i, v in enumerate(o[:3]):
            print("%s[%d]" % (pad, i))
            walk(v, depth + 1, path)
        if len(o) > 3:
            print("%s… 他 %d件" % (pad, len(o) - 3))


walk(d)
