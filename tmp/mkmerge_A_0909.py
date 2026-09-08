# -*- coding: utf-8 -*-
"""A判定2件（同じ公演日・同じ会場＝券種違い）の統合入力を作る。
   公演日・会場・県は**既存のまま据え置く**（同じ公演なので広がらない）。"""
import io, json, re, sys

sys.stdout.reconfigure(encoding="utf-8")

built = {e["id"]: e for e in json.load(io.open("tmp/sweep_rest_built.json", encoding="utf-8"))}
mp = json.load(io.open("tmp/sweep_mergemap_0909.json", encoding="utf-8"))
s = io.open("index.html", encoding="utf-8").read()
evs = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", s, re.S).group(1))
by = {e["id"]: e for e in evs}

out = []
for r in mp:
    b, e = built[r["newid"]], by[r["target"]]
    pia = (b.get("links") or {}).get("pia")
    tks = []
    for t in b.get("tickets") or []:
        t = dict(t)
        if not t.get("url"):
            t["url"] = pia          # 🚨会場別ぴあURLを焼き込む
        tks.append(t)
    out.append({
        "id": e["id"],
        "date": e["date"], "dateLabel": e["dateLabel"],
        "venue": e["venue"], "prefecture": e["prefecture"],
        "links": {"pia": (e.get("links") or {}).get("pia") or pia},
        "tickets": tks,
    })
    print("id%-5s %s ／ %s" % (e["id"], e.get("name"), e["date"]))
    for t in tks:
        print("   + %s | %s" % (t["type"], t["url"]))

io.open("tmp/merge_built_A_0909.json", "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))
