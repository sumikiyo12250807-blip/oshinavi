# -*- coding: utf-8 -*-
"""音楽スイープ(rlsStatus=0102)の未掲載106件を、
  A) 完全新規（同名の既存エントリなし）→ build_pia_entries の入力形（newid/artist/urls）
  B) 同名の既存エントリあり → 統合を検討する一覧
に分ける。newid は index.html の最大id+1 から連番（既存idは動かさない）。"""
import re, json, io

SRC = "tmp/presale_01_0905.json"
OUT_A = "tmp/newbuild_in_0905.json"
OUT_B = "tmp/samename_cand_0905.txt"

h = open("index.html", encoding="utf-8").read()
EV = json.loads(re.search(r"const EVENTS = (\[.*?\]);\n", h, re.S).group(1))
nid = max(e["id"] for e in EV) + 1

cands = json.load(io.open(SRC, encoding="utf-8"))["new"]
fresh = [x for x in cands if not x.get("name_in_db")]
same = [x for x in cands if x.get("name_in_db")]

# 同じ artist の候補は1つのエントリにまとめる（ツアーは1エントリ＝feedback_tour_consolidate）
by_artist = {}
for x in fresh:
    by_artist.setdefault(x["artist"], []).append(x["url"])

out = []
for artist, urls in by_artist.items():
    out.append({"newid": nid, "artist": artist, "urls": sorted(set(urls))})
    nid += 1
json.dump(out, io.open(OUT_A, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

buf = ["同名の既存エントリがある候補 %d件（＝ツアーの別公演の可能性。統合を検討する）" % len(same), ""]
grp = {}
for x in same:
    grp.setdefault(x["artist"], []).append(x)
for artist, xs in sorted(grp.items()):
    buf.append("■ %s … %d件" % (artist, len(xs)))
    for x in xs:
        buf.append("    %s %s | %s | 発売%s | %s"
                   % (x.get("saletype", ""), x.get("perfdate", ""), x.get("venue", ""),
                      x.get("rlsdate", ""), x.get("url", "")))
    buf.append("")
io.open(OUT_B, "w", encoding="utf-8").write("\n".join(buf))

print("FRESH_ROWS=%d -> ENTRIES=%d (id %s-%s) / SAMENAME_ROWS=%d ARTISTS=%d"
      % (len(fresh), len(out), out[0]["newid"] if out else "-", out[-1]["newid"] if out else "-",
         len(same), len(grp)))
