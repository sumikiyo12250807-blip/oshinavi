# -*- coding: utf-8 -*-
"""id7115 Tani Yuuki の取りこぼし4枠を既存エントリに足す入力を作る。
🚨 build_pia_entries が ticket.url を付けないので、bundleのURLを焼き込む
   （空のまま足すとカードから買いに行けない＝feedback_build_pia_multiurl_loses_ticket_url）。
"""
import io, json

URL = "https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670885"
d = json.load(io.open("tmp/built_7115_0907.json", encoding="utf-8"))
out = []
for e in d:
    ts = []
    for t in e.get("tickets", []):
        t = dict(t)
        if not t.get("url"):
            t["url"] = URL
        ts.append(t)
    out.append({"id": e["id"], "artist": e.get("artist"), "links": {}, "tickets": ts})
json.dump(out, io.open("tmp/merge_7115_0907.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("枠 %d に url を焼き込んだ" % sum(len(o["tickets"]) for o in out))
