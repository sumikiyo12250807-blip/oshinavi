# -*- coding: utf-8 -*-
"""取りこぼし回収のビルド結果（仮ID 9004..9008）を、本来のエントリidにまとめ直す。

merge_apply は built を id でキーにするので、同じ既存idに当てる複数のビルドは
先に tickets をまとめておく必要がある（そうしないと最後の1本しか残らない）。
"""
import json, io, collections

MAP = {
    9004: 4489,   # ASKA 福岡12/23・長崎12/25・熊本12/26
    9005: 4500,   # MONO NO AWARE 新潟3/12・長野3/14
    9006: 4500,   # MONO NO AWARE 石川3/13
    9007: 668,    # 佐藤竹善 岡山12/2
    9008: 668,    # 佐藤竹善 福岡12/22・12/23
}

# 🚨 build_pia_entries は ticket.url を付けてくれないことがある
#    （feedback_build_pia_multiurl_loses_ticket_url）。飛び先が無い枠を足すと
#    カードから買いに行けなくなるので、投げた元のURLをここで焼き込む。
URL = {
    9004: "https://t.pia.jp/pia/event/event.do?eventCd=2626038",
    9005: "https://t.pia.jp/pia/event/event.do?eventCd=2630608",
    9006: "https://t.pia.jp/pia/event/event.do?eventCd=2630609",
    9007: "https://t.pia.jp/pia/event/event.do?eventCd=2627004",
    9008: "https://t.pia.jp/pia/event/event.do?eventCd=2628756",
}

built = json.load(io.open("tmp/built_recover_0907.json", encoding="utf-8"))
out = collections.OrderedDict()

for b in built:
    tgt = MAP.get(b["id"])
    if not tgt:
        continue
    if tgt not in out:
        out[tgt] = {"id": tgt, "artist": b.get("artist"), "links": {}, "tickets": []}
    for t in b.get("tickets", []):
        if not t.get("url"):
            t["url"] = URL[b["id"]]
        out[tgt]["tickets"].append(t)

res = list(out.values())
json.dump(res, io.open("tmp/merge_recover_0907.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)

for r in res:
    print("id=%s 足す枠 %d" % (r["id"], len(r["tickets"])))
    for t in r["tickets"]:
        print("   + %s | %s" % (t.get("type"), t.get("url")))
