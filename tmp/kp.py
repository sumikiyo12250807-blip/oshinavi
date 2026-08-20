import re,json
src=open('index.html',encoding='utf-8').read()
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',src,re.S)
data=json.loads(m.group(1))
for e in data:
    if e.get('id')==871:
        print(json.dumps(e,ensure_ascii=False,indent=2))
