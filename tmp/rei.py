import re,json
src=open('index.html',encoding='utf-8').read()
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',src,re.S)
data={e['id']:e for e in json.loads(m.group(1))}
e=data[922]
print("name",e.get('name'),"| date",e.get('date'),"| venue",e.get('venue'),"| pref",e.get('prefecture'))
print("dateLabel",e.get('dateLabel'))
print("links.pia",(e.get('links') or {}).get('pia'))
for t in e.get('tickets',[]):
    print("  -",t.get('type'),"| date",t.get('date'),"| sd",t.get('startDate'),"| url",t.get('url'))
