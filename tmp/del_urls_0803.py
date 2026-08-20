# -*- coding: utf-8 -*-
"""削除候補のURLを index.html の links / tickets[].url から機械抽出する（手書き厳禁）。"""
import re, json, io, sys
sys.stdout.reconfigure(encoding='utf-8')

ENDED = [105, 342, 466, 472, 473, 1887, 2255, 2309, 2532, 2558, 2740, 3100, 3221]
ZERO  = [129, 491, 812, 976, 1593, 1664, 1689, 1970, 2204, 2329, 2656, 2848, 3419]
OTHER = [3227]

h = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
evs = {e['id']: e for e in json.loads(m.group(2))}

for label, ids in (('公演終了済', ENDED), ('ぴあ0枠', ZERO), ('ぴあ以外', OTHER)):
    print('=== %s %d件 ===' % (label, len(ids)))
    for i in ids:
        e = evs.get(i)
        if not e:
            print('  id=%s 見つからない' % i); continue
        lk = {k: v for k, v in (e.get('links') or {}).items() if v}
        turls = sorted(set(t['url'] for t in (e.get('tickets') or []) if t.get('url')))
        print('  id=%d | %s | %s | %s' % (i, e.get('name'), e.get('venue'), e.get('date')))
        for k, v in lk.items():
            if k == 'amazon':
                continue
            print('      %s: %s' % (k, v))
        for u in turls:
            print('      ticket: %s' % u)
    print()
