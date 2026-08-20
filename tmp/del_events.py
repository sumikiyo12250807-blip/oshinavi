# -*- coding: utf-8 -*-
import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
ids=[19,29,35,37,72,88,100,117,121,162,310,328,340,377,378,472,473,609,610,626,651,679,729,734]
text=open('events.html',encoding='utf-8').read()
removed=[]
for eid in ids:
    m=re.search(r'"id":\s*'+str(eid)+r',',text)
    if not m: print('NOTFOUND',eid);continue
    idpos=m.start()
    bo=text.rfind('{',0,idpos)
    depth=0;i=bo
    while i<len(text):
        c=text[i]
        if c=='{':depth+=1
        elif c=='}':
            depth-=1
            if depth==0:break
        i+=1
    close=i
    s=bo
    while s>0 and text[s-1] in ' \t':s-=1
    if s>0 and text[s-1]=='\n':s-=1
    e=close+1
    if text[e:e+1]==',':e+=1
    text=text[:s]+text[e:]
    removed.append(eid)
open('events.html','w',encoding='utf-8').write(text)
print('events削除:',len(removed),removed)
