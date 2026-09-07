# -*- coding: utf-8 -*-
"""島津亜矢の未登録 eventCd から build_pia_entries の入力を作る。
🚨 URLは kwgap の出力（＝ぴあの検索結果）から機械で抜く。手で書かない・創作しない。
   別イベント（レジェンダリー・カウント・ベイシー・オーケストラ）は名前で弾く。
"""
import io, re, json

src = io.open("tmp/kwgap_0907.txt", encoding="utf-8").read()
sec = src.split("=== tmp/kw_shimazu_0907.txt ===")[1]

cand, skipped = [], []
nid = 9200
for m in re.finditer(r"🚨未登録 (\w+)\n\s*\[(.*?)\] (.*?)\n\s*(.*?)\n\s*(\S+)\n", sec):
    cd, state, name, when, url = m.groups()
    if "島津亜矢" not in name:
        skipped.append((cd, name))
        continue
    cand.append({"newid": nid, "artist": "島津亜矢",
                 "urls": ["https://t.pia.jp/pia/event/event.do?eventCd=%s" % cd]})
    nid += 1

json.dump(cand, io.open("tmp/cand_shimazu_0907.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("候補 %d件（id %s..%s）" % (len(cand), cand[0]["newid"], cand[-1]["newid"]))
for cd, n in skipped:
    print("  別イベントとして除外: %s %s" % (cd, n[:40]))
