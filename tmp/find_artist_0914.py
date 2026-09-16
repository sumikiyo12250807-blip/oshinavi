# -*- coding: utf-8 -*-
"""名前の一部で登録済みエントリを探し、枠（券種名・締切）を並べる（読むだけ）。
削除の検証で「ツアーの続きが別の公演コードで売られている」と言われた時に、うちに登録済みかを確かめる用。
使い方: python tmp/find_artist_0914.py "名前1" "名前2" ...
出力: tmp/find_artist_0914.txt
"""
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')


def n(s):
    return re.sub(r'\s+', '', unicodedata.normalize('NFKC', s or '')).lower()


src = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
out = []
for q in sys.argv[1:]:
    hits = [e for e in ev if n(q) in n(e.get('artist')) or n(q) in n(e.get('name'))]
    out.append('#### 「%s」 %d件' % (q, len(hits)))
    for e in hits:
        out.append('== id%s [%s] %s ／ date=%s ／ %s' % (e['id'], e.get('genre'), e.get('name'), e.get('date'), e.get('venue')))
        for t in e.get('tickets') or []:
            out.append('     %s | date=%s%s' % (t.get('type'), t.get('date'), ' soldout' if t.get('soldout') else ''))
io.open('tmp/find_artist_0914.txt', 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('→ tmp/find_artist_0914.txt')
