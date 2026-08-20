import re,json
src=open('index.html',encoding='utf-8').read()
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',src,re.S)
data=json.loads(m.group(1))
news=[e for e in data if e.get('genre')=='new']
out=[]
for e in news:
    links=e.get('links',{}) or {}
    url=links.get('pia') or links.get('rakuten') or links.get('eplus') or links.get('lawson') or ''
    tk=[]
    for t in e.get('tickets',[]):
        tk.append({'type':t.get('type'),'date':t.get('date'),'startDate':t.get('startDate'),'saleUntilSoldOut':t.get('saleUntilSoldOut')})
    out.append({'id':e['id'],'name':e.get('name'),'venue':e.get('venue'),'url':url,'tickets':tk})
json.dump(out,open('tmp/audit_input.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
# split into 6 batches
import math
n=6
per=math.ceil(len(out)/n)
for b in range(n):
    chunk=out[b*per:(b+1)*per]
    json.dump(chunk,open(f'tmp/audit_batch_{b}.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print(f"batch {b}: {len(chunk)} 件  ids={[c['id'] for c in chunk]}")
