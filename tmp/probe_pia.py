import urllib.request, re, io, sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    return urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
url='https://t.pia.jp/pia/event/event.do?eventCd=2606479'
h=fetch(url)
print('HTML length:',len(h))
# look for 受付状況 labels
for kw in ['抽選受付中','受付中','発売前','受付終了','予定枚数終了','販売期間中','販売終了','プリセール','一般発売','先行']:
    print(f'  「{kw}」出現:',h.count(kw))
print('--- ticketInformation / status blocks sample ---')
# find blocks around status words
for m in list(re.finditer(r'(発売前|抽選受付中|販売期間中|予定枚数終了|販売終了|受付終了)',h))[:6]:
    s=max(0,m.start()-120); print(repr(re.sub(r'\s+',' ',h[s:m.start()+30]))[:200])
