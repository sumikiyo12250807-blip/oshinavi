# -*- coding: utf-8 -*-
"""投入したバッチを .claude/state/last_batch.json に記録する（翌朝の再チェックで使う）。

使い方: python tmp/record_batch_0910.py <id_from> <id_to> <件数> "<note>"
"""
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
PATH = '.claude/state/last_batch.json'

id_from, id_to, count = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
note = sys.argv[4]

d = json.load(io.open(PATH, encoding='utf-8'))
d['batches'].append({
    'date': '2026-09-10',
    'slot': 'morning',
    'id_from': id_from,
    'id_to': id_to,
    'count': count,
    'source': 'ぴあ 発売前スイープ rlsStatus=0102/0202（9バケツとも最終ページまで到達・rc=0）＋受付中0101の残りタネ',
    'assigned': False,
    'rechecked': False,
    'note': note,
})
json.dump(d, io.open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print('記録したわ: id %d〜%d / %d件' % (id_from, id_to, count))
