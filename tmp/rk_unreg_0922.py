# -*- coding: utf-8 -*-
"""楽天 post-sitemap の「これから発売／販売中」のうち、index.html に楽天URLが無いものを数える。"""
import io, json, re, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
src = io.open('index.html', encoding='utf-8').read()
data = json.load(io.open('tmp/rakuten_presale.json', encoding='utf-8'))
rows = [dict(r, status=k) for k in ('presale','onsale') for r in data[k]]
if isinstance(data, dict) and not rows:
    print('keys:', list(data.keys())[:20])
n = 0
for r in rows:
    st = r.get('status') or r.get('state') or ''
    if st in ('past', 'unreadable', '過去', '読めない', 'soldout_only'):
        continue
    u = r.get('url') or ''
    m = re.search(r'/(rt[0-9a-z]+)/?', u)
    key = m.group(1) if m else u
    if key and key in src:
        continue
    n += 1
    print(st, '|', (r.get('title') or r.get('name') or '')[:50], '|', u)
print('未登録らしい', n)
