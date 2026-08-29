# -*- coding: utf-8 -*-
"""e+のキーワード検索の生HTMLに埋まっているJSONから公演を取り出す。"""
import sys,re,json,io,urllib.request,urllib.parse,html
sys.stdout.reconfigure(encoding='utf-8')
kw=sys.argv[1]
out=sys.argv[2] if len(sys.argv)>2 else 'tmp/eplus_out.json'
u='https://eplus.jp/sf/search?keyword='+urllib.parse.quote(kw)
req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
h=urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
io.open(out+'.html','w',encoding='utf-8').write(h)
print('len',len(h))
# <script id="json"> or type=application/json
found=[]
for m in re.finditer(r'<script[^>]*id="[^"]*json[^"]*"[^>]*>(.*?)</script>',h,re.S|re.I):
    found.append(m.group(1))
for m in re.finditer(r'<script[^>]*type="application/(?:ld\+)?json"[^>]*>(.*?)</script>',h,re.S|re.I):
    found.append(m.group(1))
print('json blocks',len(found))
data=[]
for f in found:
    try: data.append(json.loads(html.unescape(f.strip())))
    except Exception as e: pass
io.open(out,'w',encoding='utf-8').write(json.dumps(data,ensure_ascii=False,indent=1))
print('parsed',len(data))
