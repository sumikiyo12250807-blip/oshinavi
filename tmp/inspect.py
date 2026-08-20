import re, json
ids=[935,923,933,893,906,912,913,926,934]
src=open('index.html',encoding='utf-8').read()
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',src,re.S)
data=json.loads(m.group(1))
for e in data:
    if e.get('id') in ids:
        print("id",e['id'],"|",e.get('name','')[:35])
        print("  venue:",e.get('venue','')[:40],"| links.pia:",(e.get('links',{}) or {}).get('pia'))
        for t in e.get('tickets',[]):
            print("   -",t.get('type','')[:48],"| date",t.get('date'),"| sUSO",t.get('saleUntilSoldOut'),"| sEU",t.get('saleEndUnknown'),"| url",(t.get('url','') or '')[-10:])
