# -*- coding: utf-8 -*-
"""index.html の子ども向け（genre が kids）のエントリを 番号｜名義｜公演名 で書き出す（2026-09-15 夜）
ユーザー「ニルスのふしぎな旅だったらそのニルスの塗り絵を張ったり、プリキュアだったらプリキュアの玩具だったり、それぞれのボタンを作って」
使い方: python kids_list_0915.py  → tmp/btn_tpl/kids_list.txt
"""
import re

rows, cur = [], {}
with open('index.html', encoding='utf-8') as f:
    for line in f:
        m = re.match(r'\s*"(id|artist|name|genre)":\s*(.+?),?\s*$', line)
        if not m:
            continue
        k, v = m.group(1), m.group(2).strip().rstrip(',').strip('"')
        if k == 'id':
            cur = {'id': v}
        else:
            cur[k] = v
        if k == 'genre' and v == 'kids':
            rows.append(cur)
with open('tmp/btn_tpl/kids_list.txt', 'w', encoding='utf-8') as f:
    for r in rows:
        f.write('%s｜%s｜%s\n' % (r.get('id', '?'), r.get('artist', ''), r.get('name', '')))
print('kids', len(rows))
