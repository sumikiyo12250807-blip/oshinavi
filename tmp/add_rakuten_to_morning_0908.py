# -*- coding: utf-8 -*-
"""朝ルーチンに「楽天の再照合」を足す（project_rakuten_make_it_ironclad の4番目）。

ぴあは reconcile_pia を毎朝回しているのに、楽天は**一度も回していなかった**。
2026-09-08 に手で回したら 15件中 1件が本物の誤り（別公演の枠がまぎれ込み）だった＝
**回せば出る。回していないから出ていなかっただけ。**
"""
import io

P = ".claude/skills/day/SKILL.md"
s = io.open(P, encoding="utf-8").read()

anchor = "3.5. \U0001f6a8\U0001f6a8**バッジ0の番人** `node tools/check_zero_badge.js`"
assert s.count(anchor) == 1

add = """3.4. \U0001f6a8**楽天の再照合** `python tools/reconcile_rakuten.py --ids <楽天リンクを持つid>`
   （2026-09-08 追加・[[project_rakuten_make_it_ironclad]] の4番目）
   - 対象idは `python tmp/rakuten_state_0908.py` が出す（いまは15件・22枠）
   - 🚨**ぴあと同じ理由で毎朝要る**＝登録した表示値がページとズレても、他のどの道具も気づかない。
     ヒールはぴあ専用、reconcile_pia は楽天を見ない、check_zero_badge は「枠0」しか見ない
   - 見るのは FAIL だけでなく**未照合の枠数**も（QC 0＝全部正しい、ではない）
   - ⏭️照合対象外＝楽天チケットmini形式（/mini/events/）。**目視でしか確かめられない**

"""

s = s.replace(anchor, add + anchor, 1)
io.open(P, "w", encoding="utf-8").write(s)
print("朝ルーチンに 3.4 を足した")
