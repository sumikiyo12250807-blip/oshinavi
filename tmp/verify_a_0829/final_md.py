# -*- coding: utf-8 -*-
import json,re,os
D='C:/Users/user/oshinavi/tmp/verify_a_0829'
rs=json.load(open(D+'/report.json',encoding='utf-8'))
def genre(t):
    m=re.search(r'\u30c1\u30b1\u30c3\u30c8\u3074\u3042\[(.*?)\u306e\u30c1\u30b1\u30c3\u30c8\u8cfc\u5165',t or '')
    return m.group(1) if m else ''
def name(t):
    return re.sub(r'\s*\|\s*\u30c1\u30b1\u30c3\u30c8\u3074\u3042\[.*$','',t or '')
L=[]
for r in rs:
    L.append('## id %s'%r['id'])
    L.append('- 入力URL: '+' / '.join(r['input']))
    for e in r['events']:
        L.append('- [EVENT] %s'%e['url'])
        L.append('  - name: %s'%name(e.get('title_tag','')))
        L.append('  - genre: %s'%genre(e.get('title_tag','')))
        L.append('  - period: %s'%e.get('period',''))
        L.append('  - venues: %s'%' / '.join(v for v in e.get('venue_list',[]) if '\u6ce8\u610f\u4e8b\u9805' not in v)[:400])
        for c in e['cards']:
            L.append('  - CARD %s | tag=%s | show=%s | %s(%s) | STATUS=%s | %s'%(
                c['name'],c['tags'],c.get('date_text',''),c['venue'],c['pref'],c['status_text'],c['url']))
    tim={t['url']:t for t in r['ti']}
    for u,t in tim.items():
        L.append('  - [TI] %s :: %s :: window=%s :: perf=%s'%(u,t['label'],' | '.join(t['window']),
            ' ; '.join('%s@%s'%(a,b) for a,b in t.get('perf_pairs',[])) or ','.join(t['perf_dates'])))
    L.append('')
open(D+'/final_src.md','w',encoding='utf-8').write('\n'.join(L))
print('ok',len(L))
