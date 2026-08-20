import re, json
src = open('index.html',encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\]);', src, re.S)
data = json.loads(m.group(1))
for e in data:
    if e.get('id')==602:
        print(json.dumps(e.get('links',{}),ensure_ascii=False))
        for t in e.get('tickets',[]):
            print(t.get('type','')[:50],'| url=',t.get('url',''))
