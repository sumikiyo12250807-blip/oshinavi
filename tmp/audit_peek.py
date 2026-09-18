# -*- coding: utf-8 -*-
import re, json, io, sys
src = io.open(r'C:\Users\user\oshinavi\index.html', encoding='utf-8').read()
m = re.search(r'  const EVENTS = (\[.*?\]);', src, re.S)
print('matched', bool(m))
ev = json.loads(m.group(1))
print('total', len(ev))
tg = [e for e in ev if isinstance(e.get('links'), dict) and e['links'].get('tiget')]
print('tiget', len(tg))
ids = [e['id'] for e in tg]
print('id range', min(ids), max(ids))
rng = [e for e in ev if 11317 <= e.get('id', 0) <= 13230]
print('id 11317-13230 count', len(rng))
print('in-range without tiget link', len([e for e in rng if not (isinstance(e.get('links'),dict) and e['links'].get('tiget'))]))
print('tiget outside range', len([e for e in tg if not (11317 <= e['id'] <= 13230)]))
out = io.open(r'C:\Users\user\oshinavi\tmp\audit_sample.json','w',encoding='utf-8')
json.dump(tg[:4] + tg[900:903], out, ensure_ascii=False, indent=1)
out.close()
# key frequency
from collections import Counter
c = Counter()
for e in tg:
    for k in e: c[k]+=1
print('keys', c.most_common())
tc = Counter()
for e in tg:
    for t in e.get('tickets', []) or []:
        for k in t: tc[k]+=1
print('ticket keys', tc.most_common())
