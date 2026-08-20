# -*- coding: utf-8 -*-
"""投入セットを確定する。

  除外 3859 中田カウス   ← 既存 id1098 が同じ枠を持っている
  除外 3860 さやかミニ落語会 ← 既存 id2880 が同じ枠を持っている
  除外 3865 THEカルテット  ← 既存 id2735(松戸9月)と同じシリーズ。既存へ統合する
  除外 3874 宝塚『ポーの一族』← 既存 id130 が同じ bundle・同じ枠を持っている
  追加 3875 タイムトラベラーズ・ワイフ / 3876 平成中村座 十月大歌舞伎
"""
import json, io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

DROP = {3859, 3860, 3865, 3874}
base = json.load(open("tmp/all_new_0806.json", encoding="utf-8-sig"))
add = [e for e in json.load(open("tmp/built_add_0806.json", encoding="utf-8-sig"))
       if e["id"] not in DROP]
out = [e for e in base if e["id"] not in DROP] + add
ids = sorted(e["id"] for e in out)
assert len(ids) == len(set(ids))
json.dump(out, open("tmp/all_new_0806_final.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("投入セット確定 %d件 / 枠 %d" % (len(out), sum(len(e.get("tickets") or []) for e in out)))
print("id: %s" % ", ".join(str(i) for i in ids))
