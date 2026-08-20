# -*- coding: utf-8 -*-
import re,sys,io,urllib.request,urllib.parse,collections
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
u='https://eplus.jp/sf/search?keyword='+urllib.parse.quote('Ken Yokoyama')
h=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=60).read().decode('utf-8','replace')
m=re.search(r'"koen_detail_url_pc":"(/sf/detail/[0-9A-Za-z\-]+)"',h)
blk=h[max(0,m.start()-4000):m.end()+4000]
print(blk[:8000])
