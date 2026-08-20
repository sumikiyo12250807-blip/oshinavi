import re,json
src=open('index.html',encoding='utf-8').read()
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',src,re.S)
data=json.loads(m.group(1))
news=[e for e in data if e.get('genre')=='new']
rows=[]
for e in news:
    links=e.get('links',{}) or {}
    url=links.get('pia') or links.get('rakuten') or links.get('eplus') or links.get('lawson') or ''
    # per-ticket urls?
    turls=[t.get('url') for t in e.get('tickets',[]) if t.get('url')]
    typ='bundle' if 'eventBundleCd' in url else ('event' if 'eventCd' in url else ('other' if url else 'NONE'))
    rows.append((e['id'], typ, len(e.get('tickets',[])), len(turls), url, e.get('name','')))
# write to tsv for agents
with open('tmp/audit_list.tsv','w',encoding='utf-8') as f:
    for r in rows:
        f.write('\t'.join(str(x) for x in r)+'\n')
print("total new:",len(rows))
from collections import Counter
print("by url type:",Counter(r[1] for r in rows))
print("\n=== bundleURL かつ ticket数1（多公演取りこぼし疑い）===")
for r in rows:
    if r[1]=='bundle' and r[2]==1:
        print(r[0], r[4].split('=')[-1], '| t=',r[2])
print("\n=== URL無し ===")
for r in rows:
    if r[1]=='NONE':
        print(r[0])
