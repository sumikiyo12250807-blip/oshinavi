# -*- coding: utf-8 -*-
"""ハナレグミの島根公演のエントリを探して、ジャンルと出どころを出す。"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
h = io.open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'const EVENTS = (\[.*?\]);\r?\n', h, re.S).group(1))
for e in EV:
    blob = (e.get('name') or '') + (e.get('artist') or '')
    if 'ハナレグミ' in blob:
        print('=' * 60)
        for k in ('id', 'name', 'artist', 'genre', '_genre', '_srcgenre', '_piaSub',
                  'date', 'dateLabel', 'venue', 'prefecture'):
            if k in e:
                print('%-11s = %r' % (k, e.get(k)))
        for i, t in enumerate(e.get('tickets', []), 1):
            print('  [%d] %s' % (i, t.get('type')))
            print('      startDate=%s date=%s' % (t.get('startDate'), t.get('date')))
            print('      url=%s' % t.get('url'))
        print('  links=', json.dumps(e.get('links', {}), ensure_ascii=False))
