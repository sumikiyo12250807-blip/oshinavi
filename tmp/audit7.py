# -*- coding: utf-8 -*-
import io, json, re
OUT = []
ROOT = r'C:\Users\user\oshinavi'
src = io.open(ROOT + r'\index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
by = {e['id']: e for e in EVENTS}
for i in (12212, 12346, 12362, 12477, 12491, 12625, 12767, 13054, 13228, 11396):
    e = by.get(i)
    if not e:
        continue
    OUT.append('--- id%s %s / %s / %s / %s' % (i, e['name'][:40], e['date'], e['venue'][:24],
                                               e.get('prefecture')))
    OUT.append('    links=%s' % e['links'].get('tiget'))
    for t in e['tickets']:
        OUT.append('    %s' % json.dumps(t, ensure_ascii=False))
raw = {}
for f in ('tiget_yt_vt2_0918.json', 'tiget_wide_0918.json'):
    d = json.load(io.open(ROOT + r'\tmp\\' + f, encoding='utf-8'))
    for ev in d['events']:
        raw.setdefault(str(ev['id']), ev)
OUT.append('')
OUT.append('=== 生データ側 ===')
for i in (12346, 12767, 13228):
    e = by.get(i)
    ids = sorted(set(re.findall(r'/events/(\d+)', json.dumps(e, ensure_ascii=False))))
    for x in ids:
        r = raw.get(x)
        if not r:
            continue
        OUT.append('--- events/%s %s venue=%s offers=%s' % (x, r['name'][:36], r['venue'],
                                                            [o.get('valid_from') for o in (r.get('ld_offers') or [])][:3]))
        for p in r['programs']:
            OUT.append('    公演 %s (%s)' % (p.get('date'), p.get('datetime_text')[:30]))
            for t in p.get('tickets') or []:
                OUT.append('       %r price=%s class=%s periods=%s'
                           % (t.get('name'), t.get('price'), t.get('class'),
                              [(pp.get('pay'), pp.get('text')) for pp in (t.get('periods') or [])]))
io.open(ROOT + r'\tmp\audit7_out.txt', 'w', encoding='utf-8').write('\n'.join(OUT))
