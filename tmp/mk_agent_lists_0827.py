# -*- coding: utf-8 -*-
import json,re,io,sys
sys.stdout.reconfigure(encoding='utf-8')
h=open('index.html',encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',h,re.S)
EV=[e for e in json.loads(m.group(2)) if 5332<=e['id']<=5431]
EV.sort(key=lambda e:e['id'])
half=(len(EV)+1)//2
for n,part in enumerate([EV[:half],EV[half:]],1):
    o=io.open('tmp/agentlist_%d_0827.txt'%n,'w',encoding='utf-8')
    for i,e in enumerate(part,1):
        o.write('%d. %s\n'%(i,(e.get('links') or {}).get('pia')))
    o.close()
    print('list',n,len(part))
# 未照合4枠を含むid
print('要重点確認 id: 5345,5356,5367,5395,5412')
