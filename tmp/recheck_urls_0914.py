# -*- coding: utf-8 -*-
"""前日(9/13)に入れた新着のうち、ぴあ由来のものを id と ぴあURL だけにして2つに割る
（独立再導出用・登録値は出さない）。
使い方: python tmp/recheck_urls_0914.py
出力: tmp/recheck_[AB]_0914.txt
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
LO, HI = 8347, 8384  # 9/13 の朝に入れた範囲（last_batch.json）＋楽天の投入分

src = open('index.html', encoding='utf-8').read()
m = re.search(r'  const EVENTS = (\[.*?\]);', src, re.S)
events = json.loads(m.group(1))
rows, nonpia, assigned = [], [], []
for e in events:
    if not (LO <= e['id'] <= HI):
        continue
    if e.get('genre') != 'new':
        assigned.append(e['id'])
        continue
    L = e.get('links') or {}
    urls = []
    if L.get('pia'):
        urls.append(L['pia'])
    for t in e.get('tickets') or []:
        u = t.get('url') or ''
        if 'pia.jp' in u and u not in urls:
            urls.append(u)
    if not urls:
        nonpia.append(e['id'])
        continue
    rows.append((e['id'], urls))
rows.sort()
k = 2
size = (len(rows) + k - 1) // k
for j, name in enumerate('AB'):
    part = rows[j * size:(j + 1) * size]
    with open('tmp/recheck_%s_0914.txt' % name, 'w', encoding='utf-8') as f:
        for i, urls in part:
            f.write('%s\t%s\n' % (i, ' '.join(urls)))
    if part:
        print(name, len(part), part[0][0], '-', part[-1][0])
print('ぴあ由来 %d件 / ぴあURL無し %s / 振り分け済み %s' % (len(rows), nonpia, assigned))
