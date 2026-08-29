# -*- coding: utf-8 -*-
"""rlsIn を外した一覧に『31日より先に発売』の発売前行が入っているかを実測する。"""
import re,sys,time,urllib.request,html,datetime,collections
sys.stdout.reconfigure(encoding='utf-8')
TODAY=datetime.date(2026,8,27)
def get(u):
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=30) as r:
        if 'sorry.pia' in r.geturl(): return None
        return r.read().decode('utf-8','replace')
cnt=collections.Counter(); far=[]
alld=[]
for pg in [1,5,20,40,60,80,100]:
    h=get('https://t.pia.jp/pia/rlsInfo.do?lg=01&page=%d'%pg)
    if h is None:
        print('page=%d SORRY'%pg); time.sleep(8); continue
    t=re.sub(r'<script.*?</script>','',h,flags=re.S)
    t=re.sub(r'<[^>]+>','\n',t); t=html.unescape(t)
    for st in ['販売期間中','抽選受付中','発売前','先着受付中','受付前']:
        cnt[st]+=len(re.findall(st,t))
    for a,b,c in re.findall(r'発売前\s*(\d{4})/(\d{1,2})/(\d{1,2})',t):
        d=datetime.date(int(a),int(b),int(c)); alld.append(d)
        if (d-TODAY).days>30: far.append(d)
    time.sleep(2)
print('状態の出現数(サンプル7ページ):',dict(cnt))
if alld:
    print('発売前サンプル %d件  最遅=%s (+%d日)'%(len(alld),max(alld),(max(alld)-TODAY).days))
    print('31日より先に発売＝%d件  例:'%len(far), sorted(set(far))[:8])
