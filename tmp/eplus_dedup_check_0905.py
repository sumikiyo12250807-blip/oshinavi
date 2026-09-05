# -*- coding: utf-8 -*-
import json, io, re
cands = json.load(io.open('tmp/eplus_live_cand_0905.json', encoding='utf-8'))
hh = io.open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS\s*=\s*(\[.*?\]);', hh, re.S)
db = json.loads(m.group(1))
blob = json.dumps(db, ensure_ascii=False)
already, fresh = [], []
for c in cands:
    eid = c['eid']
    hit = eid in blob
    (already if hit else fresh).append(c)
print('CAND=%d ALREADY_BY_EID=%d FRESH=%d' % (len(cands), len(already), len(fresh)))
json.dump(fresh, io.open('tmp/eplus_fresh_0905.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
for c in already:
    print('DUP eid=%s' % c['eid'])
