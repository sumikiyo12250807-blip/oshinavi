# -*- coding: utf-8 -*-
import json, os, re
BASE = r'C:/Users/user/oshinavi'
out = json.load(open(os.path.join(BASE,'tmp','verify_out_2_0825.json'), encoding='utf-8'))
print('ids=%d  errors=%d' % (len(out), sum(1 for v in out.values() if 'error' in v)))
print('buyable==0:', [k for k,v in out.items() if v.get('buyable')==0])
print()
for k,v in out.items():
    if 'error' in v: print(k,'ERROR',v['error']); continue
    for s in v['slots']:
        issues=[]
        if not s['title'].strip(): issues.append('title空')
        if not s['when'].strip(): issues.append('when空')
        if not s['venue'].strip(): issues.append('venue空')
        if not s['perfdate']: issues.append('公演日空')
        if not (s['pref'] or '').strip(): issues.append('県空')
        print('%s [%s] %s | when=%s | 公演=%s~%s | %s | pref=%s %s' % (
            k, s['state'], s['title'][:40], s['when'], s['perfdate'], s['perf_end'], s['venue'][:45], s['pref'], ('<<< '+','.join(issues)) if issues else ''))
