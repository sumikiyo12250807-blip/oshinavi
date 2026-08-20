# -*- coding: utf-8 -*-
"""怪談スイープの残り2件を作る。

  id44   稲川淳二 … 既存は長野1公演(e+枠)だけ。ぴあbundle b2665530 に【17枠の全国ツアー】がある
                    → ぴあから作り直して育成する（[[feedback_tour_consolidate]]）
  id3804 【動画配信】松原タニシの怪談七十物語 … b2668442 は会場公演(id958)ではなく配信版＝別エントリ
                    （[[feedback_streaming_events_included]]／既存 id3209 の【動画配信】と同じ扱い）
"""
import io
import json
import os
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
ROOT = r"C:\Users\user\oshinavi"

cands = [
    {"newid": 44, "artist": "稲川淳二",
     "urls": ["https://t.pia.jp/pia/event/event.do?eventBundleCd=b2665530"]},
    {"newid": 3804, "artist": "【動画配信】松原タニシの怪談七十物語",
     "urls": ["https://t.pia.jp/pia/event/event.do?eventBundleCd=b2668442"]},
]
json.dump(cands, io.open(os.path.join(ROOT, "tmp", "kaidan_grow_cands.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("→ tmp/kaidan_grow_cands.json （2件）")
