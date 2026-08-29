import json
D='C:/Users/user/oshinavi/tmp/verify_a_0829'
rs=json.load(open(D+'/report.json',encoding='utf-8'))
L=[]
for r in rs:
    L.append('#### id %s'%r['id'])
    L.append('input: '+' | '.join(r['input']))
    if r['missing']: L.append('!! MISSING PAGES: '+' | '.join(r['missing']))
    if r['ti_missing']: L.append('!! MISSING TI: '+' | '.join(r['ti_missing']))
    for e in r['events']:
        if not e.get('ok'): continue
        L.append('  [EVENT] %s'%e['url'])
        L.append('   title: %s'%e.get('title_tag',''))
        L.append('   period: %s'%e.get('period',''))
        L.append('   venues: %s'%' / '.join(e.get('venue_list',[])[:6]))
        for c in e['cards']:
            L.append('   - CARD %s | tags=%s | 公演日=%s | %s(%s) | %s [%s] ended_list=%s | %s'%(
                c['name'],c['tags'],','.join(sorted(set(c['show_dates']))),c['venue'],c['pref'],
                c['status_text'],c['status_class'],c['in_ended_list'],c['url']))
    for t in r['ti']:
        if not t.get('ok'):
            L.append('  [TI-FAIL] %s'%t['url']); continue
        L.append('  [TI] %s'%t['url'])
        L.append('    h1: %s'%t['h1'])
        L.append('    crumb: %s'%t['breadcrumb'])
        L.append('    label: %s'%t['label'])
        L.append('    window: %s'%' ;; '.join(t['window']))
        L.append('    perf_dates: %s'%','.join(t['perf_dates']))
        L.append('    venues: %s'%' / '.join(t['venues'][:12]))
        L.append('    pairs: %s'%' ; '.join('%s@%s'%(a,b) for a,b in t.get('perf_pairs',[])[:40]))
    L.append('')
open(D+'/dump.txt','w',encoding='utf-8').write('\n'.join(L))
print('lines',len(L))
