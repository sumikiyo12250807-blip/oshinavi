# -*- coding: utf-8 -*-
import io, json, re, os
from collections import Counter
TODAY = '2026-09-18'
ROOT = r'C:\Users\user\oshinavi'
raw = {}
for f in ('tiget_yt_vt2_0918.json', 'tiget_wide_0918.json'):
    d = json.load(io.open(os.path.join(ROOT, 'tmp', f), encoding='utf-8'))
    for ev in d['events']:
        raw.setdefault(str(ev['id']), ev)
src = io.open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
TG = [e for e in EV if 11317 <= e.get('id', 0) <= 13228]
reg = set()
for e in TG:
    reg |= set(re.findall(r'/events/(\d+)', json.dumps(e, ensure_ascii=False)))
skip = {}
for f in ('built_wide_0918.json', 'built_tiget_0918.json', 'built_tiget2_0918.json', 'built_tiget3_0918.json'):
    p = os.path.join(ROOT, 'tmp', f)
    if not os.path.exists(p):
        continue
    for s in (json.load(io.open(p, encoding='utf-8')).get('skipped') or []):
        skip[str(s['id'])] = s['why']
L = []
# イベント丸ごと落ち（枠が読めない）のうち validFrom が未来か
c = Counter()
for i, r in raw.items():
    if i in reg or skip.get(i) != '枠が読めない':
        continue
    offs = sorted({o['valid_from'] for o in (r.get('ld_offers') or []) if o.get('valid_from')})
    has = any(p.get('tickets') for p in r['programs'])
    if not has:
        c['券種が取れていない'] += 1
    elif len(offs) == 1 and offs[0] >= TODAY:
        c['発売日が1つ・今日以降＝そのまま出せる'] += 1
    elif len(offs) == 1:
        c['発売日が1つだが過去＝ページが矛盾（受付前なのに発売済み）'] += 1
    else:
        c['発売日が食い違う・無い'] += 1
L.append('== イベント丸ごと落ちた78件 ==')
for k, v in c.most_common():
    L.append('   %s: %d件' % (k, v))
# 枠単位
c2 = Counter()
for e in TG:
    for i in sorted(set(re.findall(r'/events/(\d+)', json.dumps(e, ensure_ascii=False)))):
        r = raw.get(i)
        if not r:
            continue
        offs = sorted({o['valid_from'] for o in (r.get('ld_offers') or []) if o.get('valid_from')})
        for p in r['programs']:
            if not p.get('date') or p['date'] < TODAY:
                continue
            for t in p.get('tickets') or []:
                if 'is-unopened' in (t.get('class') or '') and not [
                        x for x in (t.get('periods') or []) if x.get('parsed')]:
                    if len(offs) == 1 and offs[0] >= TODAY:
                        c2['発売日が1つ・今日以降＝そのまま出せる'] += 1
                    elif len(offs) == 1:
                        c2['発売日が1つだが過去＝ページが矛盾'] += 1
                    else:
                        c2['手がかり無し'] += 1
L.append('== 登録エントリの中で落ちた50枠 ==')
for k, v in c2.most_common():
    L.append('   %s: %d枠' % (k, v))
io.open(os.path.join(ROOT, 'tmp', 'audit12_out.txt'), 'w', encoding='utf-8').write('\n'.join(L))
