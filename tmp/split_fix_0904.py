# -*- coding: utf-8 -*-
"""「統合先が複数」に落ちた件のうち、名前で行き先がはっきりするものだけ候補にする。

統合する:
  2633613 名探偵プリキュア！ドリームステージ♪石川公演 → id450（ツアー束ね。41は長野単独）
  2632249 YAMATO String Quartet             → id2912（4521は「yama」＝別アーティストの誤マッチ）

新規エントリにする（既存の72＝アナ雪／96＝バック・トゥ・ザ・フューチャーのどちらでもない）:
  劇団四季「リトルマーメイド」／舞浜 … 本体＋セット券2種を1エントリに（3URLを渡す）

保留（既存が分裂していて、まず既存同士の整理が要る）:
  SHERBETS[6281,6282] / syrup16g[5526-5528] / SCANDAL[6284-6286] /
  スターダスト☆レビュー[2047,2114,4496] / 堂島孝平[4044,4518] / みゆな[5342,5343] /
  センダイガールズ[2626,4934] / 日本フィル芸劇シリーズ[1837,6462]
"""
import json, io, re

tri = json.load(io.open("tmp/_triage_0904.json", encoding="utf-8"))["samename"]
by_cd = {}
for it in tri:
    m = re.search(r"event(?:Bundle)?Cd=(\w+)", it.get("url") or "")
    if m:
        by_cd[m.group(1)] = it

MERGE = {"2633613": 450, "2912": None}
merge_cand = []
for cd, into in (("2633613", 450), ("2632249", 2912)):
    it = by_cd.get(cd)
    if not it:
        print("NOT FOUND %s" % cd); continue
    merge_cand.append({"newid": 940000 + into, "artist": it.get("artist", ""),
                       "urls": [it["url"]], "_merge_into": into})
json.dump(merge_cand, io.open("tmp/split_merge_cand_0904.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

# 劇団四季リトルマーメイド＝3つのURLを1エントリにまとめる
LM = ["b2666906", "2632085", "2632083"]
urls = []
for cd in LM:
    it = by_cd.get(cd)
    if it:
        urls.append(it["url"])
new_cand = []
if urls:
    new_cand.append({"newid": 6800, "artist": "劇団四季「リトルマーメイド」／舞浜", "urls": urls})
json.dump(new_cand, io.open("tmp/split_new_cand_0904.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)

print("MERGE_CAND=%d  NEW_CAND=%d (urls=%d)" % (len(merge_cand), len(new_cand), len(urls)))
