# -*- coding: utf-8 -*-
"""判定A（名前は同じだが別公演）の8件を新エントリとして投入する入力を作る。
🚨 build_pia_entries は ticket.url を付けないことがあるので、投げた元URLを焼き込む
   （feedback_build_pia_multiurl_loses_ticket_url）。"""
import io, json

# エージェントの独立判定 A＝8件（⚠️の7405 和田唱は既存4612が壊れている疑いがあるので保留）
KEEP = [7339, 7353, 7371, 7372, 7392, 7394, 7404, 7413]

cand = {c["newid"]: c["urls"][0] for c in json.load(io.open("tmp/cand0101_0908.json", encoding="utf-8"))}
built = {e["id"]: e for e in json.load(io.open("tmp/built0101_0908.json", encoding="utf-8"))}

out, nfill, miss = [], 0, []
for i in KEEP:
    e = built.get(i)
    if not e:
        miss.append(i)
        continue
    e = dict(e)
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

json.dump(out, io.open("tmp/inject_a0101_0908.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for e in out:
    print("id%s %s tickets=%d" % (e["id"], (e.get("name") or "")[:28], len(e["tickets"])))
print("投入 %d件 / url焼き込み %d枠 / 見つからず %s" % (len(out), nfill, miss))
