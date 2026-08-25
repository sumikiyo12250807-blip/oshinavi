# -*- coding: utf-8 -*-
import json, os, re, io, sys
ROOT = r'C:/Users/user/oshinavi'
items = json.load(open(os.path.join(ROOT,'tmp/verify_in_1_0825.json'), encoding='utf-8'))
OUTDIR = os.path.join(ROOT,'tmp/v1_0825')
PREFS = ['北海道','青森','岩手','宮城','秋田','山形','福島','茨城','栃木','群馬','埼玉','千葉','東京','神奈川','新潟','富山','石川','福井','山梨','長野','岐阜','静岡','愛知','三重','滋賀','京都','大阪','兵庫','奈良','和歌山','鳥取','島根','岡山','広島','山口','徳島','香川','愛媛','高知','福岡','佐賀','長崎','熊本','大分','宮崎','鹿児島','沖縄']
def norm_pref(p, venue):
    p = (p or '').strip()
    for x in PREFS:
        if p.startswith(x) or p == x or x in p:
            return x
    for x in PREFS:
        if x in (venue or ''):
            return x
    return p or ''
out = {}
notes = []
zero = []
for it in items:
    eid = str(it['id'])
    f = os.path.join(OUTDIR,'v_%s.json'%eid)
    try:
        rows = json.load(open(f, encoding='utf-8'))
    except Exception as e:
        out[eid] = {'error':'parse_fail: %s'%e}
        continue
    if not isinstance(rows, list):
        out[eid] = {'error':'bad_shape'}
        continue
    if len(rows) == 0:
        out[eid] = {'error':'no_ticket_cards_on_page'}
        notes.append('%s: page has 0 ticket cards'%eid)
        continue
    buy = [r for r in rows if r.get('state') in ('受付中','発売前')]
    slots = []
    prefs = []
    dates = []
    seen_soft = {}
    for r in buy:
        pd = r.get('perf_end') or r.get('perfdate') or ''
        if pd: dates.append(pd)
        pf = norm_pref(r.get('pref'), r.get('venue'))
        if pf and pf not in prefs: prefs.append(pf)
        if not (r.get('title') or '').strip():
            notes.append('%s: empty title (state=%s when=%s)'%(eid, r.get('state'), r.get('when')))
        k = (r.get('title'), r.get('when'), r.get('venue'), r.get('perfdate'), r.get('perf_end'))
        seen_soft[k] = seen_soft.get(k, 0) + 1
        slots.append({'title': r.get('title',''), 'when': r.get('when',''),
                      'venue': r.get('venue',''), 'perfdate': r.get('perfdate',''),
                      'perf_end': r.get('perf_end',''), 'state': r.get('state',''),
                      'pref': pf, 'url': r.get('url','')})
    for k,v in seen_soft.items():
        if v > 1:
            notes.append('%s: same-looking slot x%d (different urls): %s | %s'%(eid, v, k[0], k[1]))
    ent = {'buyable': len(buy),
           'last_perf': max(dates) if dates else None,
           'prefs': prefs,
           'total_cards': len(rows),
           'slots': slots}
    out[eid] = ent
    if len(buy) == 0:
        zero.append(eid)
json.dump(out, open(os.path.join(ROOT,'tmp/verify_out_1_0825.json'),'w',encoding='utf-8'), ensure_ascii=False, indent=1)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
print('entries:', len(out))
print('errors:', [k for k,v in out.items() if 'error' in v])
print('zero_buyable:', zero)
print('--- notes ---')
for n in notes: print(n)
