import re, json
ids=[110,115,337,428,602,876]
src=open('index.html',encoding='utf-8').read()
m=re.search(r'const EVENTS = (\[.*?\]);',src,re.S)
data=json.loads(m.group(1))
for e in data:
    if e.get('id') in ids:
        print("="*60)
        print("id",e['id'],e.get('name'))
        print("date",e.get('date'),"startDate",e.get('startDate'),"venue",e.get('venue'))
        for i,t in enumerate(e.get('tickets',[])):
            print(f"  [{i}] type={t.get('type')!r} date={t.get('date')} startDate={t.get('startDate')} saleUntilSoldOut={t.get('saleUntilSoldOut')} url={t.get('url','')[-12:]}")
