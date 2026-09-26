import json,sys
sys.path.insert(0,'tools')
from check_expired import extract_events_array
a=set(json.load(open('tmp/x0926/del_ids.json')));b=set(json.load(open('tmp/x0926/agent_del_ids.json')))
E={e['id']:e for e in extract_events_array('index.html')}
print('mine only',len(a-b),'agent only',len(b-a),'both',len(a&b))
for i in sorted(a-b)[:70]:
    e=E[i]; tk=e.get('tickets') or []
    print(i,e.get('date'),e.get('startDate'),e.get('longrun'),(e.get('title') or e.get('artist',''))[:28],'|',e.get('dateLabel','')[:30],'|',[ (t.get('type','')[:30],t.get('date'),t.get('startDate')) for t in tk[:2]])
for i in sorted(b-a): print('AGENT',i)
