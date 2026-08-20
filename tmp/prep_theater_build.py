import json,io,sys,re,math
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
# max id
src=open('index.html',encoding='utf-8').read()
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',src,re.S)
data=json.loads(m.group(1))
maxid=max(e['id'] for e in data)
print('現在の最大id =',maxid,'→ 新規は',maxid+1,'から')
# first 50 deduped
dd=json.load(open('tmp/theater_dedup.json',encoding='utf-8'))
batch=dd[:50]
# assign provisional ids
for i,o in enumerate(batch):
    o['newid']=maxid+1+i
# split into 5 batches of 10
n=5; per=10
for b in range(n):
    chunk=batch[b*per:(b+1)*per]
    json.dump(chunk,open(f'tmp/tbuild_{b}.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
    print(f'tbuild_{b}: {len(chunk)}件 id {chunk[0]["newid"]}-{chunk[-1]["newid"]}')
print('id範囲全体:',batch[0]['newid'],'-',batch[-1]['newid'])
