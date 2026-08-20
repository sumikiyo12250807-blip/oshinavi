import json,re
entries=json.load(open('tmp/theater3_entries.json',encoding='utf-8'))
src=open('index.html',encoding='utf-8',newline='').read()
nl='\r\n' if '\r\n' in src else '\n'
text=src.replace('\r\n','\n')
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',text,re.S)
data=json.loads(m.group(1))
# existing eventCds
ex=set()
for e in data:
    for v in (e.get('links') or {}).values():
        mm=re.search(r'event(?:Bundle)?Cd=(\w+)',str(v) or ''); ex.add(mm.group(1)) if mm else None
dups=[]
for e in entries:
    mm=re.search(r'event(?:Bundle)?Cd=(\w+)',e['links'].get('pia') or '')
    if mm and mm.group(1) in ex: dups.append(e['id'])
print('既存と重複の疑い:',dups)
# genre table + strip
gt=[]
for e in entries:
    g=e.pop('_genre','engeki'); e['genre']='new'; gt.append(f"{e['id']}\t{g}\t{e.get('name','')}")
open('tmp/genre_table_theater3.tsv','w',encoding='utf-8').write('\n'.join(gt)+'\n')
def fmt(o):
    s=json.dumps(o,ensure_ascii=False,indent=2); return '\n'.join('  '+l for l in s.split('\n'))
i0=text.index('const EVENTS = [');br=text.index('[',i0);depth=0;i=br
while i<len(text):
    if text[i]=='[':depth+=1
    elif text[i]==']':
        depth-=1
        if depth==0:break
    i+=1
block=',\n'.join(fmt(e) for e in entries)
text=text[:i].rstrip()+',\n'+block+'\n'+text[i:]
ids=[e['id'] for e in entries]
text=re.sub(r'const NEW_ORDER = \[[0-9,]*\];','const NEW_ORDER = ['+','.join(map(str,ids))+'];',text)
open('index.html','w',encoding='utf-8',newline='').write(text.replace('\n',nl))
print('injected',len(entries),'/ NEW_ORDER',len(ids))
