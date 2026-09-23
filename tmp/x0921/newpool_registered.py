# -*- coding: utf-8 -*-
"""9/21夜の新着（FANY/ZAIKO）の名前で index.html の登録を洗い出す（読むだけ）。
使い方: python tmp/x0921/newpool_registered.py
出力: tmp/x0921/newpool_registered.txt
"""
import io
import json
import re
import sys
import unicodedata

sys.stdout.reconfigure(encoding='utf-8')
KWS = ['青木マッチョ', 'OWV', '空前メテオ', 'ジョックロック', '例えば炎', 'NMB48',
       'MUSCLE BEACH', 'Verrückt', 'Verruckt', 'unchained']


def n(s):
    return unicodedata.normalize('NFKC', s or '').lower()


h = io.open('index.html', encoding='utf-8', newline='').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
o = io.open('tmp/x0921/newpool_registered.txt', 'w', encoding='utf-8')
for kw in KWS:
    hits = [e for e in ev if n(kw) in n(json.dumps({k: e.get(k) for k in ('name', 'artist', 'venue')}, ensure_ascii=False))]
    o.write('## %s  %d件\n' % (kw, len(hits)))
    for e in sorted(hits, key=lambda x: x.get('date') or ''):
        urls = sorted({t.get('url') for t in e.get('tickets') or [] if t.get('url')})
        o.write('- id%s [%s] %s ｜%s ｜%s ｜%s ｜枠%d ｜links=%s\n' % (
            e['id'], e.get('genre'), e.get('date'), (e.get('name') or '')[:60], (e.get('artist') or '')[:30],
            e.get('venue'), len(e.get('tickets') or []), json.dumps(e.get('links') or {}, ensure_ascii=False)[:200]))
        for u in urls[:6]:
            o.write('    %s\n' % u)
o.close()
print('ok')
