# -*- coding: utf-8 -*-
import sys,re,json,urllib.request,urllib.parse,html
sys.stdout.reconfigure(encoding='utf-8')
kw=sys.argv[1]
u='https://eplus.jp/sf/search?keyword='+urllib.parse.quote(kw)
req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
h=urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
print('len',len(h))
open('tmp/eplus_kw.html','w',encoding='utf-8').write(h)
# JSON-LD / 埋め込みJSONから公演名らしきものを拾う
for m in re.finditer(r'"(?:eventName|name|title)"\s*:\s*"([^"]{4,80})"',h):
    print('-',m.group(1))
