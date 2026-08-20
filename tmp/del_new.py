import re,json
src=open('index.html',encoding='utf-8',newline='').read()
nl='\r\n' if '\r\n' in src else '\n'
text=src.replace('\r\n','\n'); lines=text.split('\n')
# ids to delete = current genre:new (the just-injected batch3)
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',text,re.S)
data=json.loads(m.group(1))
delids={e['id'] for e in data if e.get('genre')=='new'}
def span(eid):
    pat=re.compile(r'^\s*"id":\s*'+str(eid)+r'\s*,')
    idx=next((i for i,l in enumerate(lines) if pat.match(l)),None)
    if idx is None:return None
    s=idx
    while lines[s].strip()!='{':s-=1
    oi=len(lines[s])-len(lines[s].lstrip());e=idx
    while e<len(lines):
        st=lines[e].strip();ind=len(lines[e])-len(lines[e].lstrip())
        if st in('}','},') and ind==oi and e>s:break
        e+=1
    return s,e
sp=sorted((span(i) for i in delids),reverse=True)
for s,e in sp:
    del lines[s:e+1]
text='\n'.join(lines)
text=re.sub(r'const NEW_ORDER = \[[0-9,]*\];','const NEW_ORDER = [];',text)
open('index.html','w',encoding='utf-8',newline='').write(text.replace('\n',nl))
print('削除',len(delids),'件',sorted(delids)[:3],'...')
