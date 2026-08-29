# -*- coding: utf-8 -*-
"""受付中(0101)＋抽選受付中(0201)の総在庫を7ジャンルで測る（読むだけ）。"""
import re,sys,time,urllib.request
sys.stdout.reconfigure(encoding='utf-8')
LG={'01':'音楽','02':'演劇','03':'スポーツ','04':'映画','05':'アート','06':'イベント','07':'クラシック'}
def tot(lg,f):
    u='https://t.pia.jp/pia/rlsInfo.do?lg=%s&%s&page=1'%(lg,f)
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
    for _ in range(3):
        with urllib.request.urlopen(req,timeout=30) as r:
            if 'sorry.pia' in r.geturl(): time.sleep(8); continue
            b=r.read().decode('utf-8','replace')
        m=re.search(r'全([\d,]+)件中',b)
        return int(m.group(1).replace(',','')) if m else 0
    return None
S=[0,0]
print('%-8s %10s %10s'%('ジャンル','受付中0101','抽選0201'))
for lg,name in LG.items():
    a=tot(lg,'rlsStatus=0101'); time.sleep(2)
    b=tot(lg,'rlsStatus=0201'); time.sleep(2)
    print('%-8s %10s %10s'%(name,a,b)); S[0]+=a or 0; S[1]+=b or 0
print('%-8s %10d %10d  合計%d'%('合計',S[0],S[1],S[0]+S[1]))
