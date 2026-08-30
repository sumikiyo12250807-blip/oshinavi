# -*- coding: utf-8 -*-
import json,io,sys,collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
d=json.load(open('tmp/_agentP1_parsed.json',encoding='utf-8'))
cnt=collections.Counter()
for eid,v in d.items():
    for c in v['cards']:
        cnt[(c['state'],c['cls'],c['st'])]+=1
print('== 状態文言の分布 ==')
for k,n in sorted(cnt.items(),key=lambda x:-x[1]):
    print(n,k)
