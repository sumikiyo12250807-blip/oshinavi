import re,json,math
src=open('index.html',encoding='utf-8').read()
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',src,re.S)
data=json.loads(m.group(1))
ids=set(range(987,1037))-{1010,1023}
out=[]
for e in data:
    if e['id'] in ids:
        links=e.get('links',{}) or {}
        main=links.get('pia') or ''
        turls=[t.get('url') for t in e.get('tickets',[]) if t.get('url')]
        urls=[main]+[u for u in turls if u and u!=main]
        out.append({'id':e['id'],'name_hint':e.get('name'),'urls':urls})
out.sort(key=lambda x:x['id'])
n=5; per=math.ceil(len(out)/n)
for b in range(n):
    chunk=out[b*per:(b+1)*per]
    json.dump(chunk,open(f'tmp/v2_{b}.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print(f'v2_{b}: {len(chunk)}件 ids={[c["id"] for c in chunk]}')
print('total',len(out))
