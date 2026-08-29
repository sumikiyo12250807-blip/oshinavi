# -*- coding: utf-8 -*-
import json, re, sys
sys.path.insert(0, 'tmp/vb0829')
sys.stdout.reconfigure(encoding='utf-8')
from fetch import get
from parse import cards, ti_detail

P = json.load(open('tmp/vb0829/parsed.json', encoding='utf-8'))
for e in P:
    if 'Bundle' not in e['url']:
        continue
    kids = sorted({m for s in e['slots'] for m in re.findall(r'eventCd=(\d+)', s['card']['url'])})
    inb = sorted({s['card']['url'] for s in e['slots']})
    print('== id', e['id'], e['url'])
    print('   bundleに出ている枠:', len(inb))
    for k in kids:
        u = 'https://t.pia.jp/pia/event/event.do?eventCd=%s' % k
        h = get(u)
        if not h:
            print('   child', k, 'FETCH FAIL'); continue
        cs = cards(h)
        extra = [c['url'] for c in cs if c['url'] not in inb]
        print('   child %s 枠数=%d 追加=%s' % (k, len(cs), extra or 'なし'))
        for c in cs:
            print('        -', c['title'][:60], '|', c['sttxt'][:40], '|', c['url'])
