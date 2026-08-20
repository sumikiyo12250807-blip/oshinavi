# -*- coding: utf-8 -*-
import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
dels=[110,203,256,337,448,471,866,803,978,982,988,438]
text=open('index.html',encoding='utf-8').read()
removed=[]
for eid in dels:
    m=re.search(r'\n  \{\n    "id": '+str(eid)+r',',text)
    if not m:
        print('NOTFOUND',eid);continue
    start=m.start()  # at the \n before {
    # find matching close of this object: start of '{' is m.start()+3 (\n + 2 spaces)
    bi=text.find('{',start)
    depth=0;i=bi
    while i<len(text):
        c=text[i]
        if c=='{':depth+=1
        elif c=='}':
            depth-=1
            if depth==0:break
        i+=1
    # i at closing }. Remove from start(\n) to i+1, plus trailing comma if present
    end=i+1
    if text[end:end+1]==',':
        end+=1
    text=text[:start]+text[end:]
    removed.append(eid)
open('index.html','w',encoding='utf-8').write(text)
print('removed',len(removed),removed)
