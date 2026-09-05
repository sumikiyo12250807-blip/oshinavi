# -*- coding: utf-8 -*-
"""スイープで見つかった完全新規（同名の既存が無い）を build_pia_entries の入力にする。

🚨 同じアーティストの複数公演は**1エントリにまとめる**（[[feedback_tour_consolidate]]）＝
   artist でグループ化して urls を全部渡す。1本ずつ渡すと multi=False で ticket.url が刻まれない。
🚨 idは 6987 から（別セッションが 6948〜6986 を使うため。2026-09-05 に取り決め）。
"""
import json, io, re

START_ID = 6987
cands = json.load(io.open("tmp/sweep_new_cand_0905.json", encoding="utf-8"))

grp = {}
for x in cands:
    k = x.get("artist") or x.get("name") or "?"
    grp.setdefault(k, []).append(x)

build_in, buf = [], []
nid = START_ID
for artist, xs in sorted(grp.items()):
    urls, seen = [], set()
    for x in xs:
        u = x.get("url") or ""
        mm = re.search(r"event(?:Bundle)?Cd=(\w+)", u)
        k = mm.group(1) if mm else u
        if k and k not in seen:
            seen.add(k)
            urls.append(u)
    if not urls:
        continue
    build_in.append({"newid": nid, "artist": artist, "urls": urls})
    buf.append("id%-5s %-34s 公演%d / URL%d" % (nid, artist[:34], len(xs), len(urls)))
    for x in xs:
        buf.append("        %s | %s | 発売%s" % (x.get("perfdate", ""), x.get("venue", ""), x.get("rlsdate", "")))
    nid += 1

json.dump(build_in, io.open("tmp/sweep_new_in_0905.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
io.open("tmp/sweep_new_in_0905.txt", "w", encoding="utf-8").write(
    "完全新規 %dエントリ（候補%d件）id %d〜%d\n\n" % (len(build_in), len(cands), START_ID, nid - 1) + "\n".join(buf))
print("NEW_ENTRIES=%d (候補%d件 / URL%d) id %d〜%d"
      % (len(build_in), len(cands), sum(len(b["urls"]) for b in build_in), START_ID, nid - 1))
