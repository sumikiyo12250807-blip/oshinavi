# -*- coding: utf-8 -*-
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}
for i in [326, 185, 449, 217]:
    e = byid[i]
    print('id=%d %s' % (i, e['artist']))
    print('  genre=%s startDate=%s date=%s' % (e.get('genre'), e.get('startDate'), e.get('date')))
    print('  dateLabel=%s' % e.get('dateLabel'))
    print('  links=%s' % {k: v for k, v in e['links'].items() if v})
    for t in e['tickets']:
        print('   ticket: %s' % json.dumps(t, ensure_ascii=False))
    print()
