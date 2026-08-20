# -*- coding: utf-8 -*-
"""新着プール(genre:"new")の一覧と_genre下書きを出す。"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
h = open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
pool = [e for e in EV if e.get('genre') == 'new']
print('新着プール %d件' % len(pool))
mo = re.search(r'NEW_ORDER\s*=\s*(\[[^\]]*\])', h)
if mo:
    print('NEW_ORDER %d件' % len(json.loads(mo.group(1))))
for e in sorted(pool, key=lambda x: x['id']):
    print('%d | _genre=%-8s | extra=%-16s | piaSub=%-14s | %s / %s (%s %s)' % (
        e['id'], e.get('_genre') or '-', ','.join(e.get('_extraGenres') or []) or '-',
        e.get('_piaSub') or '-', (e.get('artist') or '')[:20], (e.get('name') or '')[:30],
        e.get('prefecture', ''), e.get('date', '')))
