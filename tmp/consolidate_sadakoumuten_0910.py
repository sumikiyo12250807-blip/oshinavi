# -*- coding: utf-8 -*-
"""さだ工務店の3公演を1エントリにまとめる（[[feedback_tour_consolidate]]）。

🚨各枠に**その会場のぴあURL**を焼き込む（[[feedback_tour_per_ticket_url]]）。
   まとめたあとに url が空だと、押した人が別会場のページへ飛ぶ。
"""
import datetime
import io
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')
WD = '月火水木金土日'


def jp(s):
    y, m, d = [int(x) for x in s.split('-')]
    return '%d年%d月%d日(%s)' % (y, m, d, WD[datetime.date(y, m, d).weekday()])


built = json.load(io.open('tmp/built_sadakoumuten_0910.json', encoding='utf-8'))
cands = {c['newid']: c['urls'][0]
         for c in json.load(io.open('tmp/cand_sadakoumuten_0910.json', encoding='utf-8'))}

base = dict(built[0])
base['id'] = built[0]['id']
tickets, venues, prefs, dates = [], [], [], []
for b in built:
    u = cands[b['id']]
    for t in b['tickets']:
        t = dict(t)
        t['url'] = t.get('url') or u
        tickets.append(t)
    v = (b.get('venue') or '').strip()
    if v and v not in venues:
        venues.append(v)
    p = (b.get('prefecture') or '').strip()
    if p and p not in prefs:
        prefs.append(p)
    dates.append(b['date'])

base['tickets'] = tickets
base['venue'] = '全国ツアー（%s）' % '／'.join(venues) if len(venues) > 1 else venues[0]
base['prefecture'] = '・'.join(prefs)
base['date'] = max(dates)
base['dateLabel'] = '%s〜%s %s' % (jp(min(dates)), jp(max(dates)), base['prefecture'])

print('id=%s %s' % (base['id'], base['name']))
print('  %s' % base['dateLabel'])
print('  %s' % base['venue'])
for t in base['tickets']:
    print('   %-46s date=%s url=%s' % (t['type'][:46], t['date'], t['url'][:52]))

json.dump([base], io.open('tmp/built_sadakoumuten_one_0910.json', 'w', encoding='utf-8'),
          ensure_ascii=False, indent=1)
print('\n→ tmp/built_sadakoumuten_one_0910.json（1エントリ）')
