# -*- coding: utf-8 -*-
"""候補ファイルに newid を振る。

🚨**削除済みidを再利用しない**ので、いま index.html にある最大idだけでなく
   .claude/state/last_batch.json の過去バッチの id_to も見て、大きいほうから採番する
   （2026-09-07・09-08 に同じ配慮をしている）。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
SRC = sys.argv[1]

h = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
maxid = max(e['id'] for e in json.loads(m.group(2)))

lb = json.load(io.open('.claude/state/last_batch.json', encoding='utf-8'))
maxbatch = max((b.get('id_to') or 0) for b in lb['batches'])

start = max(maxid, maxbatch) + 1
print('index.htmlの最大id=%d / 過去バッチのid_to最大=%d → %d から採番' % (maxid, maxbatch, start))

cands = json.load(io.open(SRC, encoding='utf-8'))
for i, c in enumerate(cands):
    c['newid'] = start + i
json.dump(cands, io.open(SRC, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('%d件に newid を振ったわ（%d〜%d）' % (len(cands), start, start + len(cands) - 1))
