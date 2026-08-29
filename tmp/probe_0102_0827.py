# -*- coding: utf-8 -*-
import re,sys,time,urllib.request,datetime,html
sys.stdout.reconfigure(encoding='utf-8')
TODAY=datetime.date(2026,8,27)
def get(u):
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=30) as r:
        if 'sorry.pia' in r.geturl(): return None
        return r.read().decode('utf-8','replace')
alld=[]
for pg in [1,10,30,50,70,73]:
    h=get('https://t.pia.jp/pia/rlsInfo.do?lg=01&rlsStatus=0102&page=%d'%pg)
    if h is None: print('page',pg,'SORRY'); time.sleep(6); continue
    for a,b,c in re.findall(r'発売前\s*(\d{4})/(\d{1,2})/(\d{1,2})',h):
        alld.append(datetime.date(int(a),int(b),int(c)))
    time.sleep(2)
print('サンプル%d件 最早=%s(+%d) 最遅=%s(+%d)'%(len(alld),min(alld),(min(alld)-TODAY).days,max(alld),(max(alld)-TODAY).days))
print('31日より先に発売=%d件 (%.0f%%)'%(sum(1 for d in alld if (d-TODAY).days>30), 100*sum(1 for d in alld if (d-TODAY).days>30)/len(alld)))
