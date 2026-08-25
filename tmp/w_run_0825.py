# -*- coding: utf-8 -*-
import json, subprocess, sys, time, os, re
BASE = r'C:/Users/user/oshinavi'
IN = os.path.join(BASE, 'tmp', 'verify_in_2_0825.json')
OUT = os.path.join(BASE, 'tmp', 'verify_out_2_0825.json')
PREFS = ['北海道','青森','岩手','宮城','秋田','山形','福島','茨城','栃木','群馬','埼玉','千葉','東京','神奈川','新潟','富山','石川','福井','山梨','長野','岐阜','静岡','愛知','三重','滋賀','京都','大阪','兵庫','奈良','和歌山','鳥取','島根','岡山','広島','山口','徳島','香川','愛媛','高知','福岡','佐賀','長崎','熊本','大分','宮崎','鹿児島','沖縄']
def norm_pref(s):
    s = (s or '').strip()
    for p in PREFS:
        if s.startswith(p) or p in s:
            return p
    return s
items = json.load(open(IN, encoding='utf-8'))
res = {}
log = []
for i, it in enumerate(items):
    eid = str(it['id']); url = it['pia']
    raw = os.path.join(BASE, 'tmp', 'w_%s.json' % eid)
    err = os.path.join(BASE, 'tmp', 'w_%s.err' % eid)
    ok = False
    for attempt in range(3):
        with open(raw, 'wb') as fo, open(err, 'wb') as fe:
            rc = subprocess.call([sys.executable, os.path.join(BASE,'tools','pia_tickets.py'), url, '--all', '--json'], stdout=fo, stderr=fe)
        if rc == 0 and os.path.getsize(raw) > 0:
            ok = True; break
        time.sleep(6 * (attempt + 1))
    if not ok:
        msg = open(err, encoding='utf-8', errors='replace').read().strip().splitlines()
        res[eid] = {'error': (msg[-1] if msg else 'fetch failed rc=%d' % rc)[:300]}
        log.append('%s ERROR' % eid)
        time.sleep(2.0); continue
    try:
        rows = json.load(open(raw, encoding='utf-8'))
    except Exception as e:
        res[eid] = {'error': 'json parse: %s' % e}
        log.append('%s JSONERR' % eid); time.sleep(2.0); continue
    buy = [r for r in rows if r.get('state') in ('受付中','発売前')]
    slots = []
    for r in buy:
        slots.append({'title': r.get('title',''), 'when': r.get('when',''), 'venue': r.get('venue',''),
                      'perfdate': r.get('perfdate',''), 'perf_end': r.get('perf_end',''),
                      'state': r.get('state',''), 'pref': norm_pref(r.get('pref','')), 'url': r.get('url','')})
    dates = [d for s in slots for d in (s['perfdate'], s['perf_end']) if d]
    prefs = []
    for s in slots:
        p = s['pref'] or norm_pref(s['venue'])
        if p and p not in prefs: prefs.append(p)
    res[eid] = {'buyable': len(buy), 'total_cards': len(rows),
                'last_perf': max(dates) if dates else None,
                'first_perf': min(dates) if dates else None,
                'prefs': prefs, 'slots': slots,
                'ended_texts': sorted({r.get('statustext','') for r in rows if r.get('state') not in ('受付中','発売前')})}
    log.append('%s buyable=%d total=%d' % (eid, len(buy), len(rows)))
    time.sleep(2.0)
json.dump(res, open(OUT,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
open(os.path.join(BASE,'tmp','w_log_0825.txt'),'w',encoding='utf-8').write('\n'.join(log))
print('done', len(res))
