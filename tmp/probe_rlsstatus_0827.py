# -*- coding: utf-8 -*-
"""rlsStatus の値を総当たりして「発売前」を返すコードがあるかを実測する。"""
import re,sys,time,urllib.request
sys.stdout.reconfigure(encoding='utf-8')
def get(u):
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=30) as r:
        if 'sorry.pia' in r.geturl(): return None
        return r.read().decode('utf-8','replace')
base=None
for v in ['0101','0102','0201','0202','0301','0302','0401','01','02','03','04']:
    h=get('https://t.pia.jp/pia/rlsInfo.do?lg=01&rlsStatus=%s&page=1'%v)
    if h is None: print(v,'SORRY'); time.sleep(6); continue
    m=re.search(r'全([\d,]+)件中',h)
    tot=m.group(1) if m else '?'
    pre=len(re.findall(r'発売前',h)); act=len(re.findall(r'販売期間中',h)); lot=len(re.findall(r'抽選受付中',h))
    print('rlsStatus=%-5s 総%8s  1ページ内: 発売前%2d 販売期間中%2d 抽選受付中%2d'%(v,tot,pre,act,lot))
    time.sleep(2)
