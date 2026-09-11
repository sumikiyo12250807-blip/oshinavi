# -*- coding: utf-8 -*-
"""保留ファイル（tmp/hold_new_0912.json）から、答えが出た 8281 蒼ノトキ だけを投入用に取り出す（読むだけ・tmpに書く）。
8281＝和洋楽器ユニット「蒼ノトキ」ライブ 2027/1/21 曳舟文化センター 劇場ホール。
既存927（2026/9/26 こもれびGRAFAREホール）とは会場も年も違う別の回＝二重登録ではない（2026-09-12 朝に確認）。
使い方: python tmp/pick_8281_0912.py
出力: tmp/inject_8281_0912.json
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
hold = json.load(io.open('tmp/hold_new_0912.json', encoding='utf-8'))
pick = [b for b in hold if b['id'] == 8281]
assert len(pick) == 1, '8281 が保留ファイルに1件だけあるはず'
assert '曳舟' in (pick[0].get('venue') or ''), '8281 の会場が想定と違う'
json.dump(pick, io.open('tmp/inject_8281_0912.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('8281 %s（%s）→ tmp/inject_8281_0912.json' % (pick[0].get('name'), pick[0].get('dateLabel')))
