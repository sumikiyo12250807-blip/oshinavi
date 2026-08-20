import re,json
src=open('index.html',encoding='utf-8').read()
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',src,re.S)
data={e['id']:e for e in json.loads(m.group(1))}
e=data[874]
print("name",e.get('name'),"| date",e.get('date'),"| venue",e.get('venue'))
print("links.pia:",(e.get('links') or {}).get('pia'))
for i,t in enumerate(e.get('tickets',[])):
    print(f"[{i}]",t.get('type'),"| date",t.get('date'),"| sd",t.get('startDate'),"| url",t.get('url'))
