# -*- coding: utf-8 -*-
"""発売前スイープの新規ビルド（tmp/built_0912.json・79件）から、保留する分を外して投入用にする（読むだけ・tmpに書く）。
保留＝あたしが部分一致11件を1件ずつ見て、同じ公演の二重登録かもしれない／まとめ方を決め切れないと判断した3件:
  8264 大江千里トリオ（既存4741 大江千里と同じ2027/1/24）
  8281 和洋楽器ユニット「蒼ノトキ」ライブ 2027/1/21（既存927と同じシリーズ名）
  8322 第38回なにわ淀川花火大会（既存2535は「ぴあシート／ぴあプラチナペアシート」だけのエントリ・同じ10/17）
出力: tmp/inject_new_0912.json ／ tmp/hold_new_0912.json
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
HOLD = {8264, 8281, 8322}
built = json.load(io.open('tmp/built_0912.json', encoding='utf-8-sig'))
assert HOLD <= {b['id'] for b in built}, '保留のidがビルド結果に無い'
inject = [b for b in built if b['id'] not in HOLD]
hold = [b for b in built if b['id'] in HOLD]
json.dump(inject, io.open('tmp/inject_new_0912.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
json.dump(hold, io.open('tmp/hold_new_0912.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('新規ビルド %d件 ＝ 投入 %d ／ 保留 %d' % (len(built), len(inject), len(hold)))
