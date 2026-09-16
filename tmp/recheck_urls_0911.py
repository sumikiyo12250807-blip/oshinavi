# -*- coding: utf-8 -*-
"""新着プールのぴあ由来エントリを id と ぴあURL だけにして2つのファイルに割る（独立再導出用・登録値は出さない）。
使い方: python tmp/recheck_urls_0911.py
出力: tmp/recheck_A_0911.txt / tmp/recheck_B_0911.txt
"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

src = open('index.html', encoding='utf-8').read()
m = re.search(r'  const EVENTS = (\[.*?\]);', src, re.S)
events = json.loads(m.group(1))
SKIP = {7558}  # 保留中（一般発売の枠がぴあから消えた件）
rows = []
for e in events:
    if e.get('genre') != 'new' or e['id'] in SKIP:
        continue
    L = e.get('links') or {}
    if not L.get('pia'):
        continue
    urls = [L['pia']]
    for t in e.get('tickets') or []:
        u = t.get('url') or ''
        if 'pia.jp' in u and u not in urls:
            urls.append(u)
    rows.append((e['id'], urls))
rows.sort()
half = (len(rows) + 1) // 2
for name, part in (('A', rows[:half]), ('B', rows[half:])):
    with open('tmp/recheck_%s_0911.txt' % name, 'w', encoding='utf-8') as f:
        for i, urls in part:
            f.write('%s\t%s\n' % (i, ' '.join(urls)))
    print(name, len(part), part[0][0], '-', part[-1][0])
