# -*- coding: utf-8 -*-
import json, os, re
BASE = r'C:/Users/user/oshinavi'
res = json.load(open(os.path.join(BASE,'tmp','verify_out_2_0825.json'), encoding='utf-8'))
items = {str(i['id']): i['pia'] for i in json.load(open(os.path.join(BASE,'tmp','verify_in_2_0825.json'), encoding='utf-8'))}
bundles=[k for k,u in items.items() if 'Bundle' in u]
print('bundle_ids=', bundles)
# venue that is just a slash-separated prefecture list (no real hall name)
preflist=[]
for k,v in res.items():
    for s in v['slots']:
        ven=s['venue']
        if '／' in ven and re.fullmatch(r'[^／]*(都|府|県|北海道)(／[^／]*(都|府|県|北海道))+', ven):
            preflist.append(k)
print('venue_is_preflist=', sorted(set(preflist)))
# lottery slots
print('lottery_ids=', [k for k,v in res.items() if any('抽選' in s['statustext'] for s in v['slots'])])
# schema check
need={'buyable','last_perf','prefs','slots'}
print('schema_ok=', all(need <= set(v) or 'error' in v for v in res.values()))
print('slot_schema_ok=', all({'title','when','venue','perfdate'} <= set(s) for v in res.values() for s in v.get('slots',[])))
print('n=', len(res))
# lotRlsCd (lottery) vs rlsCd
print('lotRls_ids=', [k for k,v in res.items() if any('lotRlsCd' in s['url'] for s in v['slots'])])
