# -*- coding: utf-8 -*-
"""重複3件(3859中田カウス/3860さやか/3865THEカルテット)を抜いた分の入れ替え候補。

  3859/3860 ＝ 既存 id1098 / id2880 が同じ枠をすでに持っている＝投入不要
  3865       ＝ 既存 id2735(松戸9月)と同じシリーズ＝別エントリにせず既存へ統合する（[[feedback_tour_consolidate]]）
差し替えは演劇の大物3つ（在庫の rlsIn=03 から）。
"""
import json, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

E = "https://t.pia.jp/pia/event/event.do?eventCd=%s"
B = "https://t.pia.jp/pia/event/event.do?eventBundleCd=%s"

ROWS = [
    ("engeki", "宝塚歌劇雪組公演 ミュージカル・ゴシック『ポーの一族』", [B % "b2666575"]),
    ("engeki", "ミュージカル「タイムトラベラーズ・ワイフ」", [B % "b2670261"]),
    ("engeki", "平成中村座 十月大歌舞伎", [E % "2615521"]),
]
out = [{"newid": 3874 + i, "artist": n, "urls": u, "_srcgenre": g}
       for i, (g, n, u) in enumerate(ROWS)]
json.dump(out, open("tmp/cand_add_0806.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("入れ替え候補 %d件 → tmp/cand_add_0806.json (id 3874..3876)" % len(out))
