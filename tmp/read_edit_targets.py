import re,json
ids=[884,881,892,905,923,933,935,893,906,912,913,926,934,866,879]
src=open('index.html',encoding='utf-8').read()
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',src,re.S)
data=json.loads(m.group(1))
d={e['id']:e for e in data}
for i in ids:
    e=d.get(i)
    if not e: 
        print(i,"NOT FOUND");continue
    links=e.get('links',{}) or {}
    url=links.get('pia') or links.get('eplus') or links.get('rakuten') or ''
    print(f"--- {i} {e.get('name','')[:24]} | url={url.split('=')[-1]}")
    for t in e.get('tickets',[]):
        print(f"     type={t.get('type')} | date={t.get('date')} | startDate={t.get('startDate')} | sUSO={t.get('saleUntilSoldOut')} | url={(t.get('url') or '')[-8:]}")
