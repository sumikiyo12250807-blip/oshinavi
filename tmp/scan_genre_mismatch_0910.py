# -*- coding: utf-8 -*-
"""振り分け済みなのに、ぴあ由来の下書き(_genre)と本ジャンル(genre)が食い違うエントリを出す。

きっかけ＝2026-09-09 夜。id6972 ハナレグミが gakusai になっていた。
ぴあの区分は機械で写すのが決まり（[[feedback_genre_pia_asis_and_other]]）なので、
食い違いはどちらかが間違っている合図。
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))

rows = []
for e in events:
    g, d = e.get('genre'), e.get('_genre')
    if not d or g in (None, 'new'):
        continue
    if g != d:
        rows.append(e)

with open('tmp/genre_mismatch_0910.txt', 'w', encoding='utf-8') as f:
    f.write('genre と _genre が食い違う: %d件\n' % len(rows))
    for e in sorted(rows, key=lambda x: (x.get('genre') or '', x['id'])):
        ls = e.get('links') or {}
        u = ls.get('pia') or ls.get('eplus') or ls.get('rakuten') or ls.get('lawson') or ''
        f.write('\nid=%-5s genre=%-10s _genre=%-10s %s\n   %s\n'
                % (e['id'], e.get('genre'), e.get('_genre'), e['name'][:50], u))
print('genre と _genre が食い違う %d件 → tmp/genre_mismatch_0910.txt' % len(rows))
