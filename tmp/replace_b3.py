import json,re
entries=json.load(open('tmp/theater3_v2.json',encoding='utf-8'))
# genre table
gt=[]
for e in entries:
    g=e.pop('_genre','engeki'); e['genre']='new'; gt.append(f"{e['id']}\t{g}\t{e.get('name','')}")
open('tmp/genre_table_theater3.tsv','w',encoding='utf-8').write('\n'.join(gt)+'\n')

src=open('index.html',encoding='utf-8',newline='').read()
nl='\r\n' if '\r\n' in src else '\n'
text=src.replace('\r\n','\n'); lines=text.split('\n')
data=json.loads(re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',text,re.S).group(1))
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
for s,e in sorted((span(i) for i in delids),reverse=True):
    del lines[s:e+1]
text='\n'.join(lines)
# fix trailing comma before EVENTS close: find '},\n];' -> '}\n];'
text=re.sub(r'\}\s*,(\s*)\];', r'}\1];', text, count=1)
# inject before EVENTS ]
i0=text.index('const EVENTS = [');br=text.index('[',i0);depth=0;i=br
while i<len(text):
    if text[i]=='[':depth+=1
    elif text[i]==']':
        depth-=1
        if depth==0:break
    i+=1
def fmt(o):
    s=json.dumps(o,ensure_ascii=False,indent=2);return '\n'.join('  '+l for l in s.split('\n'))
block=',\n'.join(fmt(e) for e in entries)
text=text[:i].rstrip()+',\n'+block+'\n'+text[i:]
ids=[e['id'] for e in entries]
text=re.sub(r'const NEW_ORDER = \[[0-9,]*\];','const NEW_ORDER = ['+','.join(map(str,ids))+'];',text)
open('index.html','w',encoding='utf-8',newline='').write(text.replace('\n',nl))
print('削除',len(delids),'→ 再投入',len(entries))
