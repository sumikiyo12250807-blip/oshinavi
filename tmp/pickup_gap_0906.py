# -*- coding: utf-8 -*-
"""記事「今週のピックアップ」の取りこぼし点検。

記事は「9/7(月)〜9/13(日)にチケットの発売が始まるアーティスト紹介」と名乗っている。
その窓で発売が始まる枠を全部数えて、記事の主役5組＋タイル12組と突き合わせ、
**載せるべきなのに載っていない大物**が居ないかを見る。

大物の目安＝会場のキャパ（アリーナ・ドーム・大ホール等）。ここでは会場名で機械的に印を付けて、
判断はあたしが実物を見てする（キャパの数字はDBに無いので機械では決めない）。
"""
import json
import re
import sys
import collections

sys.stdout.reconfigure(encoding="utf-8")

FROM, TO = "2026-09-07", "2026-09-13"

# 記事に出ている組（build_section.py の MAIN と TILES から機械で取る）
bs = open("tmp/pickup0906/build_section.py", encoding="utf-8").read()
mm = re.search(r"MAIN = \[(.*?)\]\n", bs, re.S)
tt = re.search(r"TILES = \[(.*?)\]\n", bs, re.S)
main_ids = [int(x) for x in re.findall(r",\s*(\d+)\)", mm.group(1))]
tile_ids = [int(x) for x in re.findall(r",\s*(\d+)\)", tt.group(1))]
inarticle = set(main_ids) | set(tile_ids)
print("記事に出ているエントリ = 主役%d組 + タイル%d組 = %d件"
      % (len(main_ids), len(tile_ids), len(inarticle)))

h = open("index.html", encoding="utf-8").read()
m = re.search(r"(  const EVENTS = )(\[.*?\])(;)", h, re.S)
EVENTS = json.loads(m.group(2))

BIG = ["アリーナ", "ドーム", "大ホール", "国際フォーラム", "武道館", "Zepp", "ホールA",
       "サンプラザ", "オーチャード", "オペラパレス", "NHKホール", "サントリーホール",
       "東京芸術劇場", "フェスティバルホール", "オペラシティ", "ミューザ", "文化会館",
       "市民会館", "芸術劇場", "スタジアム", "コンサートホール"]

rows = []
for e in EVENTS:
    for t in e.get("tickets") or []:
        sd = t.get("startDate")
        if sd and FROM <= sd <= TO:
            rows.append((e, t, sd))
            break

print("9/7〜9/13に発売が始まるエントリ = %d件" % len(rows))
print("")

missing_big = []
for e, t, sd in rows:
    if e["id"] in inarticle:
        continue
    v = e.get("venue") or ""
    if any(b in v for b in BIG):
        missing_big.append((e, t, sd))

print("=== 記事に出ていない & 大きめの会場 = %d件（ここから漏れを探す） ===" % len(missing_big))
for e, t, sd in sorted(missing_big, key=lambda x: x[2]):
    print("  %s発売  id=%-5d %-30s @%s" % (sd, e["id"], (e.get("artist") or "")[:30],
                                          (e.get("venue") or "")[:44]))

print("")
print("=== 記事に出ている組が、本当にこの窓で発売するか ===")
byid = {e["id"]: e for e in EVENTS}
for eid in main_ids + tile_ids:
    e = byid.get(eid)
    if not e:
        print("  🚨 id=%d が index.html に無い（統合や削除で消えた可能性）" % eid)
        continue
    ok = [t for t in (e.get("tickets") or [])
          if t.get("startDate") and FROM <= t.get("startDate") <= TO]
    mark = "OK " if ok else "🚨 "
    print("  %sid=%-5d %-30s この窓の発売 %d枠" % (mark, eid, (e.get("artist") or "")[:30], len(ok)))
