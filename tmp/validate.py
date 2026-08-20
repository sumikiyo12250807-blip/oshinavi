import re, json
for path in ['index.html','events.html']:
    src=open(path,encoding='utf-8').read()
    m=re.search(r'(const EVENTS|const events|EVENTS|events)\s*=\s*(\[.*?\]);',src,re.S)
    # generic: find first '= [' big array
    m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',src,re.S)
    try:
        data=json.loads(m.group(1))
        print(path,'OK 件数=',len(data))
    except Exception as e:
        print(path,'PARSE ERROR',e)
