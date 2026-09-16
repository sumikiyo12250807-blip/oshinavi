# -*- coding: utf-8 -*-
"""新着のローチケ9件（7819〜7827）の要点と下書きジャンル（_genre/_srcgenre/_piaSub）を出す（読むだけ）。"""
import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
src = open('index.html', encoding='utf-8').read()
ev = {e['id']: e for e in json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))}
for i in range(7819, 7828):
    e = ev.get(i)
    if not e:
        print('id%s なし' % i); continue
    print('id%s [%s] _genre=%s _srcgenre=%s _piaSub=%s | %s | %s | %s' % (
        i, e.get('genre'), e.get('_genre'), e.get('_srcgenre'), e.get('_piaSub'),
        e.get('name'), e.get('dateLabel'), (e.get('links') or {}).get('lawson')))
