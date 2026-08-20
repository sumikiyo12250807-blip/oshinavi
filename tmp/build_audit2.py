import re,json,math
src=open('index.html',encoding='utf-8').read()
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',src,re.S)
data=json.loads(m.group(1))
news=[e for e in data if e.get('genre')=='new']
out=[]
for e in news:
    links=e.get('links',{}) or {}
    main=links.get('pia') or links.get('rakuten') or links.get('eplus') or links.get('lawson') or ''
    turls=[t.get('url') for t in e.get('tickets',[]) if t.get('url')]
    allurls=[main]+[u for u in turls if u and u!=main]
    tk=[{'type':t.get('type'),'date':t.get('date'),'startDate':t.get('startDate'),'saleUntilSoldOut':t.get('saleUntilSoldOut')} for t in e.get('tickets',[])]
    out.append({'id':e['id'],'name':e.get('name'),'venue':e.get('venue'),'is_bundle':('eventBundleCd' in main),'urls':allurls,'tickets':tk})
n=6; per=math.ceil(len(out)/n)
for b in range(n):
    chunk=out[b*per:(b+1)*per]
    json.dump(chunk,open(f'tmp/audit2_batch_{b}.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print(f"batch {b}: {len(chunk)}件 ids={[c['id'] for c in chunk]}")
print("total",len(out))
