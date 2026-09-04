# -*- coding: utf-8 -*-
"""新着プール93件の枠が「発売前／受付中／終了済み」のどれかをローカルで数える。
翌朝の再チェックの一段目（ネットは叩かない）。終了済みが混ざっていたら投入時の取りこぼし。"""
import json, re, io, datetime

OUT = "tmp/newpool_state_0905.txt"
TODAY = datetime.date.today().isoformat()

html = open("index.html", encoding="utf-8").read()
events = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", html, re.S).group(1))
news = sorted([e for e in events if e.get("genre") == "new"], key=lambda e: e["id"])

pre, live, dead, unknown = [], [], [], []
for e in news:
    kinds = set()
    for t in e.get("tickets", []):
        sd, d = t.get("startDate"), t.get("date")
        if t.get("soldout"):
            kinds.add("soldout")
        elif sd and sd > TODAY:
            kinds.add("pre")
        elif d and d < TODAY:
            kinds.add("dead")
        elif d:
            kinds.add("live")
        else:
            kinds.add("unknown")
    if "pre" in kinds:
        pre.append(e)
    elif "live" in kinds:
        live.append(e)
    elif "dead" in kinds:
        dead.append(e)
    else:
        unknown.append(e)

buf = ["新着プール %d件の枠の状態（today=%s・ローカル判定のみ）" % (len(news), TODAY), "",
       "  発売前を持つ … %d件" % len(pre),
       "  受付中のみ   … %d件" % len(live),
       "  🚨全部終了   … %d件" % len(dead),
       "  判定不能     … %d件" % len(unknown), ""]

for label, grp in (("🚨全部終了", dead), ("判定不能", unknown)):
    if not grp:
        continue
    buf.append("=== %s ===" % label)
    for e in grp:
        buf.append("id=%-5s %s | date=%s" % (e["id"], e.get("name", ""), e.get("date")))
        for t in e.get("tickets", []):
            buf.append("    %s | startDate=%s date=%s soldout=%s"
                       % (t.get("type"), t.get("startDate"), t.get("date"), t.get("soldout")))
        links = e.get("links") or {}
        if links.get("pia"):
            buf.append("    %s" % links["pia"])
    buf.append("")

io.open(OUT, "w", encoding="utf-8").write("\n".join(buf))
print("PRE=%d LIVE=%d DEAD=%d UNKNOWN=%d" % (len(pre), len(live), len(dead), len(unknown)))
