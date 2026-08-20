import re,json
src=open('index.html',encoding='utf-8').read()
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',src,re.S)
data=json.loads(m.group(1))
for e in data:
    if e.get('id') in (72,137):
        print("id",e['id'],e.get('name','')[:30],"| date",e.get('date'),"| longrun",e.get('longrun'))
        for t in e.get('tickets',[]):
            print("   -",t.get('type',''),"| date",t.get('date'),"| sUSO",t.get('saleUntilSoldOut'))
