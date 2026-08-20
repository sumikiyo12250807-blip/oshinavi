# -*- coding: utf-8 -*-
"""genre:new のうち「本日(2026-07-09)発売」チケットを持つ＝発売開始で締切日が要る子を洗い出す。"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
TODAY = '2026-07-09'
h = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S).group(1))
hit = []
for e in EVENTS:
    if e.get('genre') != 'new':
        continue
    todays = [t for t in e.get('tickets', []) if t.get('startDate') == TODAY]
    if todays:
        hit.append(e['id'])
        print('id=%d %s' % (e['id'], e['artist'][:30]))
        for t in e['tickets']:
            mark = ' <<本日発売' if t.get('startDate') == TODAY else ''
            print('     - %s (start=%s)%s' % (t['type'], t.get('startDate'), mark))
print('\n本日発売を含む genre:new =', len(hit))
print('ids =', ','.join(str(i) for i in hit))
