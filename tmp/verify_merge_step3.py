# -*- coding: utf-8 -*-
"""要注意グループの中身を全文表示"""
import re, json, unicodedata, sys, io, collections
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PATH = r'C:\Users\user\oshinavi\index.html'
TODAY = '2026-09-04'
src = open(PATH, encoding='utf-8', newline='').read()
EVENTS = json.loads(re.search(r'const EVENTS = (\[.*?\]);', src, re.S).group(1))
byid = {e.get('id'): e for e in EVENTS}
def visible(t):
    if t.get('saleUntilSoldOut') or t.get('soldout'): return True
    sd, d = t.get('startDate'), (t.get('date') or '')
    return not ((not sd or sd <= TODAY) and d < TODAY)

TARGETS = [
 [3858,4932,5123], [5747,5855], [2270,4527], [3984,4512], [5581,5582,5583],
 [5236,5237], [1960,1961,4732], [41,450], [6284,6285,6286], [2317,4503],
 [2987,4525], [5392,5393], [907,3115], [353,4615], [4953,4954,4955],
 [5645,5646], [6546,6547], [5296,5300], [3610,4724], [4711,4775],
 [5135,5141,5142,5147,5152],
]
KEYS = ['id','name','genre','extraGenres','area','venue','date','dateLabel','type','desc','description','subtitle','note','verified','artist','organizer']
for grp in TARGETS:
    print('#'*70)
    for i in grp:
        e = byid.get(i)
        if not e: print('  MISSING', i); continue
        print('--- id=%s %s' % (i, e.get('name')))
        for k in KEYS:
            if k in e and k not in ('id','name','tickets'):
                print('    %s: %s' % (k, e[k]))
        extra = [k for k in e.keys() if k not in KEYS and k!='tickets']
        if extra: print('    other keys: %s' % ({k:(str(e[k])[:120]) for k in extra},))
        for t in (e.get('tickets') or []):
            print('      %s type=%r label=%r start=%s end=%s sold=%s untilSold=%s' % (
                'VISIBLE' if visible(t) else '  hidden', t.get('type'), t.get('dateLabel'),
                t.get('startDate'), t.get('date'), t.get('soldout'), t.get('saleUntilSoldOut')))
            print('              url=%s' % (t.get('url'),))
    print()
