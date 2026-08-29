# -*- coding: utf-8 -*-
import re,sys,time,urllib.request
sys.stdout.reconfigure(encoding='utf-8')
LG={'01':'音楽','02':'演劇','03':'スポーツ','04':'映画','05':'アート','06':'イベント','07':'クラシック'}
def get(u):
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=30) as r:
        if 'sorry.pia' in r.geturl(): return None
        return r.read().decode('utf-8','replace')
tot_all=tot_p=0
print('%-10s %10s %10s'%('ジャンル','発売情報全部','rlsIn=03'))
for lg,name in LG.items():
    a=get('https://t.pia.jp/pia/rlsInfo.do?lg=%s&page=1'%lg); time.sleep(2)
    b=get('https://t.pia.jp/pia/rlsInfo.do?lg=%s&rlsIn=03&page=1'%lg); time.sleep(2)
    def tt(h):
        if h is None: return None
        m=re.search(r'全([\d,]+)件中',h.replace('<','<'))
        if not m:
            import html as H
            m=re.search(r'全([\d,]+)件中',H.unescape(re.sub(r'<[^>]+>','',h)))
        return int(m.group(1).replace(',','')) if m else None
    x,y=tt(a),tt(b)
    print('%-10s %10s %10s'%(name,x,y))
    if x: tot_all+=x
    if y: tot_p+=y
print('%-10s %10d %10d'%('合計',tot_all,tot_p))
