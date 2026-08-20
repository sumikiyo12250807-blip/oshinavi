import re,json
src=open('index.html',encoding='utf-8').read()
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',src,re.S)
data={e['id']:e for e in json.loads(m.group(1))}
for i in [935,884,913,881]:
    e=data[i]
    print(f"== {i} {e.get('name','')[:20]}")
    for t in e.get('tickets',[]):
        print("  ",t.get('type'),"| date",t.get('date'),"| sd",t.get('startDate'),"| url",(t.get('url') or '')[-8:])
