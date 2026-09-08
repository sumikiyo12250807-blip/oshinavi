# -*- coding: utf-8 -*-
"""判定A（既存と名前は同じだが別公演）の2件だけを新エントリとして投入する入力を作る。
🚨 build_pia_entries は ticket.url を付けないことがあるので、投げた元URLを焼き込む
   （feedback_build_pia_multiurl_loses_ticket_url）。"""
import io, json

KEEP = [7225, 7317]   # 7225 細坪基佳（日本青年館 2027/1/16）／7317 東京ヴィヴァルディ合奏団（第一生命ホール 2027/1/17）

cand = {c["newid"]: c["urls"][0] for c in json.load(io.open("tmp/cand_0908.json", encoding="utf-8"))}
built = {e["id"]: e for e in json.load(io.open("tmp/built_0908.json", encoding="utf-8"))}

out, nfill = [], 0
for i in KEEP:
    e = dict(built[i])
    src = cand.get(i) or (e.get("links") or {}).get("pia") or ""
    ts = []
    for t in e.get("tickets", []) or []:
        t = dict(t)
        if not t.get("url"):
            t["url"] = src
            nfill += 1
        ts.append(t)
    e["tickets"] = ts
    out.append(e)

json.dump(out, io.open("tmp/inject_a_0908.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for e in out:
    print("id%s tickets=%d" % (e["id"], len(e["tickets"])))
print("投入 %d件 / url焼き込み %d枠" % (len(out), nfill))
