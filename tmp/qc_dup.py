# -*- coding: utf-8 -*-
import json, collections
new = json.load(open(r'C:\Users\user\oshinavi\tmp\qc_new.json', encoding='utf-8'))
g = collections.defaultdict(list)
for e in new: g[(e.get('artist') or '')+'|'+(e.get('name') or '')].append(e)
out=[]
for k,v in g.items():
    if len(v)>1:
        gs = {x.get('_genre') for x in v}
        out.append(f"■ {k}  ({len(v)}件) _genre={sorted(gs)} {'★ジャンル割れ' if len(gs)>1 else ''}")
        for x in v:
            out.append(f"   id={x['id']} {x.get('date')} {x.get('prefecture')} {x.get('venue')} sub={x.get('_piaSub')} pia={(x.get('links') or {}).get('pia')}")
open(r'C:\Users\user\oshinavi\tmp\qc_dup.txt','w',encoding='utf-8').write('\n'.join(out))
print('ok')
