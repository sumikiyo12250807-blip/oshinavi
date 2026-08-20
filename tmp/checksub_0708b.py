# -*- coding: utf-8 -*-
import re, json, io, sys
from collections import Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
pool = [e for e in EVENTS if e.get('genre') == 'new']
c = Counter(e.get('_genre', '?') for e in pool)
print('下書き:', dict(c))
print('\n=== 判断枠(_piaSub 空 or その他) ===')
for e in sorted(pool, key=lambda x: x['id']):
    sub = e.get('_piaSub', '')
    if (not sub) or ('その他' in sub):
        print('  id=%d _genre=%s sub=\'%s\' | %s @ %s' %
              (e['id'], e.get('_genre'), sub, e['artist'][:32], e.get('venue', '')[:24]))
print('\n=== engeki下書き 全件(音楽混入チェック) ===')
for e in sorted(pool, key=lambda x: x['id']):
    if e.get('_genre') == 'engeki':
        print('  id=%d sub=\'%s\' | %s @ %s' %
              (e['id'], e.get('_piaSub', ''), e['artist'][:32], e.get('venue', '')[:24]))
