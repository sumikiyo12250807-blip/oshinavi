# -*- coding: utf-8 -*-
import json, os, re, datetime
BASE = r'C:/Users/user/oshinavi'
res = json.load(open(os.path.join(BASE,'tmp','verify_out_2_0825.json'), encoding='utf-8'))
TODAY = datetime.date(2026,8,25)
cnt={}
for v in res.values():
    for s in v['slots']:
        cnt[s['state']]=cnt.get(s['state'],0)+1
print('state_counts(ascii):', {('ONSALE' if k=='受付中' else 'PRESALE' if k=='発売前' else 'OTHER:'+repr(k)):n for k,n in cnt.items()})
st={}
for v in res.values():
    for s in v['slots']:
        st[s['statustext']]=st.get(s['statustext'],0)+1
print('statustext_counts:', {repr(k):n for k,n in st.items()})
print()
bad_deadline=[]; no_date=[]; deadline_after_perf=[]
for k,v in res.items():
    for s in v['slots']:
        m=re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', s['when'])
        if not m: no_date.append((k,s['when'])); continue
        d=datetime.date(int(m.group(1)),int(m.group(2)),int(m.group(3)))
        if d < TODAY: bad_deadline.append((k,s['when'],s['state']))
        if s['perf_end'] and d.isoformat() > s['perf_end']: deadline_after_perf.append((k,d.isoformat(),s['perf_end']))
print('deadline_unparseable=', no_date)
print('deadline_already_past=', bad_deadline)
print('deadline_after_last_perf=', deadline_after_perf)
print()
# when prefix type: tilde = deadline, otherwise sale start
pre=[]
for k,v in res.items():
    for s in v['slots']:
        w=s['when'].strip()
        kind = 'DEADLINE' if w.startswith('～') or w.startswith('〜') else 'OTHER'
        pre.append((k,kind))
from collections import Counter
print('when_kind:', Counter(x[1] for x in pre))
print('when_OTHER ids:', [k for k,x in pre if x=='OTHER'])
# how many distinct perf dates per entry
print()
print('entries_with_perf_range:', {k:(v['first_perf'],v['last_perf']) for k,v in res.items() if v['first_perf']!=v['last_perf']})
