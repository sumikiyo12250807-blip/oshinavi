# -*- coding: utf-8 -*-
"""島津亜矢の回収12件を、既存エントリ id710 に足す入力にまとめる。

🚨 build_pia_entries は ticket.url を付けないので、投げた元のURLを焼き込む
   （空のまま足すとカードから買いに行けない＝feedback_build_pia_multiurl_loses_ticket_url）。
🚨 公演範囲が広がるので date / dateLabel / venue も build 側の値に寄せる必要があるが、
   merge_apply がその更新を持っているので、ここでは tickets と links だけ渡す。
"""
import io, json

TARGET = 710
cand = {c["newid"]: c["urls"][0] for c in json.load(io.open("tmp/cand_shimazu_0907.json", encoding="utf-8"))}
built = json.load(io.open("tmp/built_shimazu_0907.json", encoding="utf-8"))

tickets, n_url = [], 0
for b in built:
    src = cand.get(b["id"], "")
    for t in b.get("tickets", []):
        t = dict(t)
        if not t.get("url"):
            t["url"] = src
            n_url += 1
        tickets.append(t)

json.dump([{"id": TARGET, "artist": "島津亜矢", "links": {}, "tickets": tickets}],
          io.open("tmp/merge_shimazu_0907.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("id%d に足す枠 %d（url焼き込み %d）" % (TARGET, len(tickets), n_url))
