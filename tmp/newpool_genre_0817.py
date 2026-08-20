# -*- coding: utf-8 -*-
"""新着プール（genre:"new"）の _genre / _piaSub / 会場 を一覧にする。振り分け前の下ごしらえ確認用。"""
import re, json, sys, io
sys.stdout.reconfigure(encoding='utf-8')
raw = io.open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', raw, re.S).group(1))
NEW = [e for e in EV if e.get('genre') == 'new']
print('新着プール %d件' % len(NEW))
for e in NEW:
    print('id%-5s | _genre=%-9s | _piaSub=%-16s | %s' % (
        e['id'], e.get('_genre') or '-', (e.get('_piaSub') or '-')[:16],
        (e.get('artist') or '')[:34]))
    print('        会場=%s (%s) | extra=%s | amazon=%s' % (
        (e.get('venue') or '')[:46], e.get('prefecture'),
        e.get('_extraGenres') or e.get('extraGenres') or '-',
        'あり' if (e.get('links') or {}).get('amazon') else 'なし'))
