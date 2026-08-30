# -*- coding: utf-8 -*-
import re,io,sys,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
h=open('index.html',encoding='utf-8',newline='').read()
m=re.search(r'const EVENTS\s*=\s*(\[)',h)
print('anchor', bool(m), m.start() if m else '')
# ブレース対応で配列を切り出す
i=m.start(1); depth=0
for j in range(i,len(h)):
    if h[j]=='[': depth+=1
    elif h[j]==']':
        depth-=1
        if depth==0: break
arr=h[i:j+1]
data=json.loads(arr)
print('EVENTS件数',len(data))
json.dump(data,open('tmp/_agentP1_events.json','w',encoding='utf-8'),ensure_ascii=False)
