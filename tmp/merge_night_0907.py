# -*- coding: utf-8 -*-
"""夜の取りこぼし回収を既存エントリへ足す入力にする。
 9300（ブランデー戦記 Zepp DiverCity 11/19 先行）→ id4045
🚨 build_pia_entries が ticket.url を付けないので、投げた元のURLを焼き込む。
"""
import io, json

MAP = {9300: 4045}
cand = {c["newid"]: c["urls"][0] for c in json.load(io.open("tmp/cand_night_0907.json", encoding="utf-8"))}
built = json.load(io.open("tmp/built_night_0907.json", encoding="utf-8"))

out, n = [], 0
for b in built:
    tgt = MAP.get(b["id"])
    if not tgt:
        continue
    ts = []
    for t in b.get("tickets", []):
        t = dict(t)
        if not t.get("url"):
            t["url"] = cand[b["id"]]
            n += 1
        ts.append(t)
    out.append({"id": tgt, "artist": b.get("artist"), "links": {}, "tickets": ts})

json.dump(out, io.open("tmp/merge_night_0907.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("統合先 %d件 / url焼き込み %d枠" % (len(out), n))
