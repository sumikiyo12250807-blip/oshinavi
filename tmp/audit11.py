# -*- coding: utf-8 -*-
import io, json, re, os
ROOT = r'C:\Users\user\oshinavi'
raw = {}
for f in ('tiget_yt_vt2_0918.json', 'tiget_wide_0918.json'):
    d = json.load(io.open(os.path.join(ROOT, 'tmp', f), encoding='utf-8'))
    for ev in d['events']:
        raw.setdefault(str(ev['id']), ev)
src = io.open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
EV = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', src, re.S).group(1))
by = {e['id']: e for e in EV}
lines = []
for i in (12744, 12561):
    e = by[i]
    for x in sorted(set(re.findall(r'/events/(\d+)', json.dumps(e, ensure_ascii=False)))):
        r = raw.get(x)
        offs = sorted({o['valid_from'] for o in (r.get('ld_offers') or []) if o.get('valid_from')})
        lines.append('id%s events/%s offers_days=%s n_offers=%d' % (i, x, offs, len(r.get('ld_offers') or [])))
io.open(os.path.join(ROOT, 'tmp', 'audit11_out.txt'), 'w', encoding='utf-8').write('\n'.join(lines))
