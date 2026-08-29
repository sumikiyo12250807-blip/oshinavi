# -*- coding: utf-8 -*-
"""発売前の本当の総在庫を rlsStatus=0102(先着・発売前)＋0202(抽選・受付前) で測る。
   従来の rlsIn=03(30日以内)と比べて何件取りこぼしていたかを出す。"""
import re,sys,time,urllib.request
sys.stdout.reconfigure(encoding='utf-8')
LG={'01':'音楽','02':'演劇','03':'スポーツ','04':'映画','05':'アート','06':'イベント','07':'クラシック'}
def tot(lg,f):
    u='https://t.pia.jp/pia/rlsInfo.do?lg=%s&%s&page=1'%(lg,f)
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
    for _ in range(3):
        with urllib.request.urlopen(req,timeout=30) as r:
            if 'sorry.pia' in r.geturl(): time.sleep(6); continue
            b=r.read().decode('utf-8','replace')
        m=re.search(r'全([\d,]+)件中',b)
        return int(m.group(1).replace(',','')) if m else 0
    return None
print('%-8s %10s %10s %10s %10s'%('ジャンル','rlsIn=03','0102発売前','0202受付前','発売前合計'))
S=[0,0,0,0]
for lg,name in LG.items():
    a=tot(lg,'rlsIn=03'); time.sleep(1.5)
    b=tot(lg,'rlsStatus=0102'); time.sleep(1.5)
    c=tot(lg,'rlsStatus=0202'); time.sleep(1.5)
    print('%-8s %10s %10s %10s %10s'%(name,a,b,c,(b or 0)+(c or 0)))
    S[0]+=a or 0; S[1]+=b or 0; S[2]+=c or 0
print('%-8s %10d %10d %10d %10d'%('合計',S[0],S[1],S[2],S[1]+S[2]))
print()
print('毎日 rlsIn=03 だけ回して取りこぼしていた発売前＝ %d件（%.0f%%）'%(S[1]+S[2]-S[0], 100*(S[1]+S[2]-S[0])/(S[1]+S[2])))
