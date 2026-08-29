# -*- coding: utf-8 -*-
import json,sys,io
sys.stdout.reconfigure(encoding='utf-8')
for p,name in [('tmp/ep_takaiwa.json','高岩遼'),('tmp/ep_akuruyo.json','明くる夜の羊')]:
    d=json.load(open(p,encoding='utf-8'))
    print('=====',name)
    def walk(o,depth=0):
        if isinstance(o,dict):
            ks=set(o.keys())
            if {'name'} & ks or {'eventName'} & ks or {'title'} & ks:
                keep={k:v for k,v in o.items() if not isinstance(v,(dict,list))}
                if keep: print(' ',json.dumps(keep,ensure_ascii=False)[:400])
            for v in o.values(): walk(v,depth+1)
        elif isinstance(o,list):
            for v in o: walk(v,depth+1)
    walk(d)
