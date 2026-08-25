# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
d = json.load(open(r'C:/Users/user/oshinavi/tmp/verify_out_1_0825.json', encoding='utf-8'))
for k,v in d.items():
    if 'error' in v: continue
    bad=[]
    if not v['prefs']: bad.append('pref空')
    if not v['last_perf']: bad.append('公演日空')
    for s in v['slots']:
        if not s['when']: bad.append('when空:'+s['title'][:20])
        if not s['perfdate']: bad.append('perfdate空:'+s['title'][:20])
        if not s['url']: bad.append('url空:'+s['title'][:20])
    print(k, 'buy=%d/%d'%(v['buyable'],v['total_cards']), 'last=%s'%v['last_perf'], '/'.join(v['prefs']), ('!! '+', '.join(sorted(set(bad))) if bad else ''))
