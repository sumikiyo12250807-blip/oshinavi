# -*- coding: utf-8 -*-
import re,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

def delete_ids(path, ids):
    text=open(path,encoding='utf-8').read()
    removed=[]
    for eid in ids:
        m=re.search(r'\n  \{\n    "id": '+str(eid)+r',',text)
        if not m:
            print(' NOTFOUND',path,eid);continue
        start=m.start()
        bi=text.find('{',start)
        depth=0;i=bi
        while i<len(text):
            c=text[i]
            if c=='{':depth+=1
            elif c=='}':
                depth-=1
                if depth==0:break
            i+=1
        end=i+1
        if text[end:end+1]==',':end+=1
        text=text[:start]+text[end:]
        removed.append(eid)
    open(path,'w',encoding='utf-8').write(text)
    return removed

dg=delete_ids('index.html',[128,434,468,652,658,1129])
print('index D削除:',len(dg),dg)
ev=delete_ids('events.html',[19,29,35,37,72,88,100,117,121,162,310,328,340,377,378,472,473,609,610,626,651,679,729,734])
print('events削除:',len(ev),ev)
