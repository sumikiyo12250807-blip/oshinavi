# -*- coding: utf-8 -*-
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
nb = json.load(open('tmp/rebuild_1869.json', encoding='utf-8'))
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
for e in EVENTS:
    if e.get('id') == 1869:
        print('before tickets:', len(e.get('tickets', [])))
        e['tickets'] = nb['tickets']   # プリセール7/4 + 一般7/10 の2枠に修正
        print('after  tickets:', len(e['tickets']))
        for t in e['tickets']:
            print('   -', t.get('type'), '| start=', t.get('startDate'), 'end=', t.get('date'))
        break
if DRY:
    print('(DRY)')
else:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0703_fix1869', 'w', encoding='utf-8').write(h)
    open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print('written (backup: index.html.bak_0703_fix1869)')
