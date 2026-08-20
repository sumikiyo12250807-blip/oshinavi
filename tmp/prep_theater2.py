import json,io,sys,re,math
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
src=open('index.html',encoding='utf-8').read()
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',src,re.S)
data=json.loads(m.group(1))
maxid=max(e['id'] for e in data)
existing_pia=set()
for e in data:
    for k,v in (e.get('links') or {}).items():
        if v and 'eventCd' in str(v): existing_pia.add(re.search(r'event(?:Bundle)?Cd=\w+',v).group(0))
    for t in e.get('tickets',[]):
        if t.get('url'): 
            mm=re.search(r'event(?:Bundle)?Cd=\w+',t['url'])
            if mm: existing_pia.add(mm.group(0))
print('max id',maxid,'→ 新規',maxid+1,'から')
dd=json.load(open('tmp/theater_dedup.json',encoding='utf-8'))
batch=dd[50:100]   # 51件目〜100件目
# skip any whose only url already in DB (eventCd dup safety)
kept=[]
for o in batch:
    cds={re.search(r'event(?:Bundle)?Cd=\w+',u).group(0) for u in o['urls'] if re.search(r'event(?:Bundle)?Cd=\w+',u)}
    if cds and cds.issubset(existing_pia):
        print('  skip(既存):',o['artist'][:24]); continue
    kept.append(o)
for i,o in enumerate(kept):
    o['newid']=maxid+1+i
n=5; per=math.ceil(len(kept)/n)
for b in range(n):
    chunk=kept[b*per:(b+1)*per]
    json.dump(chunk,open(f'tmp/t2build_{b}.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print(f't2build_{b}: {len(chunk)}件 id {chunk[0]["newid"]}-{chunk[-1]["newid"]}')
print('合計',len(kept),'件 id',kept[0]['newid'],'-',kept[-1]['newid'])
