# -*- coding: utf-8 -*-
"""rlsIn バケツごとに『発売日』の分布を実測して、31日より先の発売が入るバケツを探す。"""
import re,sys,time,urllib.request,html,datetime
sys.stdout.reconfigure(encoding='utf-8')
TODAY=datetime.date(2026,8,27)
def get(u):
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req,timeout=30) as r:
        if 'sorry.pia' in r.geturl(): return None
        return r.read().decode('utf-8','replace')
def rows(h):
    t=re.sub(r'<script.*?</script>','',h,flags=re.S)
    t=re.sub(r'<[^>]+>','\n',t); t=html.unescape(t)
    ds=re.findall(r'発売前\s*(\d{4})/(\d{1,2})/(\d{1,2})',t)
    return [datetime.date(int(a),int(b),int(c)) for a,b,c in ds]
for rls in ['03','04','05','06']:
    alld=[]
    for pg in [1,10,30,60,100]:
        h=get('https://t.pia.jp/pia/rlsInfo.do?lg=01&rlsIn=%s&page=%d'%(rls,pg))
        if h is None: print('  rlsIn=%s page=%d SORRY'%(rls,pg)); time.sleep(6); continue
        d=rows(h); alld+=d
        time.sleep(2)
    if alld:
        mn,mx=min(alld),max(alld)
        print('rlsIn=%s サンプル%d件  最早発売日=%s(+%d日)  最遅発売日=%s(+%d日)'%(
            rls,len(alld),mn,(mn-TODAY).days,mx,(mx-TODAY).days))
    else:
        print('rlsIn=%s サンプル0件'%rls)
