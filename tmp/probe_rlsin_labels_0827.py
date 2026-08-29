# -*- coding: utf-8 -*-
import re,sys,urllib.request,html
sys.stdout.reconfigure(encoding='utf-8')
req=urllib.request.Request('https://t.pia.jp/pia/rlsInfo.do?lg=01&page=1',headers={'User-Agent':'Mozilla/5.0'})
h=urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
open('tmp/rlsinfo_lg01.html','w',encoding='utf-8').write(h)
print('len',len(h))
# rlsIn を含む箇所の周辺を出す
for m in re.finditer(r'rlsIn', h):
    s=max(0,m.start()-260); e=min(len(h),m.end()+260)
    seg=html.unescape(h[s:e])
    seg=re.sub(r'\s+',' ',seg)
    print('---',seg)
