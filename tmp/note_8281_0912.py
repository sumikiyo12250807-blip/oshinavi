# -*- coding: utf-8 -*-
"""last_batch.json の 9/12 朝（id8261〜）のバッチの説明を、その後の決定に合わせて直す（index.html は触らない）。
  ・8281 蒼ノトキ＝既存927とは会場も年も違う別の回と確かめて投入済み（保留から外れた）
  ・8264 大江千里トリオ＝既存4741と同じ一般発売1枠だけの二重登録なので投入しない（4741の会期に福岡1/22を足した）
使い方: python tmp/note_8281_0912.py
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = '.claude/state/last_batch.json'
d = json.load(io.open(P, encoding='utf-8'))
ADD = (' ／9/12朝のうちに決着＝8281 蒼ノトキは既存927とは会場も年も違う別の回と確かめて投入済み（count 76→77）／'
       '8264 大江千里トリオは既存4741と同じ一般発売1枠だけの二重登録なので投入しない（4741の会期に福岡1/22を足した）。'
       '残る保留は 8322 なにわ淀川花火（既存2535はぴあシートだけのエントリ＝ユーザーに扱いを聞く）。')
n = 0
for b in d['batches']:
    if b.get('date') == '2026-09-12' and b.get('id_from') == 8261:
        if '9/12朝のうちに決着' not in (b.get('note') or ''):
            b['note'] = (b.get('note') or '') + ADD
            b['count'] = 77
        n += 1
assert n == 1, '9/12朝(id8261〜)のバッチが1つでない: %d' % n
io.open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=2) + '\n')
print('last_batch の 9/12朝(id8261〜)のバッチの説明を直した')
