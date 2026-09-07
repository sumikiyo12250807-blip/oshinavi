# -*- coding: utf-8 -*-
"""今朝投入した新着のうち、既存と同じ公演だった20件を「既存へ足す」入力JSONにする。

🚨 build_pia_entries は ticket.url を付けないことがある
   （feedback_build_pia_multiurl_loses_ticket_url）。url が空のまま既存に足すと
   **カードから買いに行けない枠**が増えるので、候補JSONの元URLを焼き込む。
出力＝tmp/merge_dup_0907.json（merge_apply_0905.py に渡す）
"""
import io, re, json

PAIRS = [
    (7105, 6601), (7108, 5729), (7110, 3129), (7112, 5052), (7120, 5436),
    (7122, 4195), (7124, 3905), (7125, 3750), (7126, 5430), (7127, 6414),
    (7134, 3514), (7142, 2694), (7148, 5421), (7149, 5408), (7150, 5409),
    (7151, 6452), (7153, 3818), (7154, 4716), (7160, 2080), (7161, 2081),
]

h = io.open("index.html", encoding="utf-8", newline="").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\r?\n", h, re.S).group(1))
by = {e["id"]: e for e in EV}

cand = {c["newid"]: c["urls"][0] for c in json.load(io.open("tmp/cand_0907.json", encoding="utf-8"))}

out, n_url = [], 0
for new_id, old_id in PAIRS:
    n, o = by.get(new_id), by.get(old_id)
    assert n and o, "id=%s / %s が現物に無い" % (new_id, old_id)
    src = cand.get(new_id) or (n.get("links") or {}).get("pia") or ""
    tickets = []
    for t in n.get("tickets", []):
        t = dict(t)
        if not t.get("url"):
            t["url"] = src
            n_url += 1
        tickets.append(t)
    out.append({"id": old_id, "artist": o.get("artist"), "links": {}, "tickets": tickets})

json.dump(out, io.open("tmp/merge_dup_0907.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
print("統合先 %d件 / 焼き込んだurl %d枠" % (len(out), n_url))
print("欠番にする新id: %s" % ",".join(str(a) for a, _ in PAIRS))
