# -*- coding: utf-8 -*-
"""楽天の発売前ハーベスト結果（tmp/rakuten_presale.json）を、登録済みかどうかで分ける（読むだけ）。
登録済み＝index.html に同じ楽天ページのURL（rtXXXX）が入っている。"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(open('tmp/rakuten_presale.json', encoding='utf-8-sig'))
h = open('index.html', encoding='utf-8').read()
rows = d if isinstance(d, list) else (d.get('presale') or d.get('items') or [])
if isinstance(d, dict):
    print('keys:', list(d.keys())[:10])
pre = [r for r in rows if (r.get('kind') or r.get('status') or '') in ('presale', '発売前')] or rows
for r in pre[:40]:
    url = r.get('url') or ''
    m = re.search(r'/(rt[0-9a-z]+)/?', url, re.I)
    code = m.group(1) if m else url
    reg = '登録済' if code and code in h else '未登録'
    print(reg, '|', (r.get('title') or r.get('name') or '')[:50], '|', url, '|', r.get('kind') or r.get('status'))
