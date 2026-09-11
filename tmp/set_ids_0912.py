# -*- coding: utf-8 -*-
"""ビルド済みエントリに正式な id を振る（削除済みidを再利用しない＝既存の最大idと last_batch の id_to の大きい方＋1から）。
使い方: python tmp/set_ids_0912.py <built.json> <出力.json>
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src, dst = sys.argv[1], sys.argv[2]
h = io.open('index.html', encoding='utf-8').read()
evs = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))
mx = max([e['id'] for e in evs] + [b.get('id_to') or 0 for b in lb['batches']])
built = json.load(io.open(src, encoding='utf-8'))
for n, e in enumerate(built):
    e['id'] = mx + 1 + n
json.dump(built, io.open(dst, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('最大id=%d → %d件に id %d..%d を振った → %s' % (mx, len(built), mx + 1, mx + len(built), dst))
