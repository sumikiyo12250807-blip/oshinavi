# -*- coding: utf-8 -*-
import io, json, re
from collections import Counter
OUT = []


def P(s=''):
    OUT.append(s)


ROOT = r'C:\Users\user\oshinavi'
raw = {}
for f in ('tiget_yt_vt2_0918.json', 'tiget_wide_0918.json'):
    d = json.load(io.open(ROOT + r'\tmp\\' + f, encoding='utf-8'))
    for ev in d['events']:
        raw.setdefault(str(ev['id']), ev)
src = io.open(ROOT + r'\index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
by = {e['id']: e for e in EVENTS}

for eid in (12104, 12744, 12066, 13066):
    e = by[eid]
    ids = sorted(set(re.findall(r'/events/(\d+)', json.dumps(e, ensure_ascii=False))))
    P('=== id%s %s （登録%d枠）' % (eid, e['name'][:40], len(e['tickets'])))
    for t in e['tickets']:
        P('    登録: %s' % t['type'])
    for i in ids:
        r = raw.get(i)
        if not r:
            continue
        for p in r['programs']:
            tk = p.get('tickets') or []
            P('    生: 公演%s %s 券種%d' % (p.get('date'), (p.get('datetime_text') or '')[:24], len(tk)))
            for t in tk[:10]:
                P('       %r price=%s class=%s per=%s' % ((t.get('name') or '')[:40], t.get('price'),
                                                          t.get('class'),
                                                          [pp.get('text') for pp in (t.get('periods') or [])][:1]))
            if len(tk) > 10:
                P('       …ほか%d枠（名前の出方=%s）'
                  % (len(tk) - 10, Counter([(t.get('name') or '')[:14] for t in tk]).most_common(4)))
    P()
io.open(ROOT + r'\tmp\audit9_out.txt', 'w', encoding='utf-8').write('\n'.join(OUT))
