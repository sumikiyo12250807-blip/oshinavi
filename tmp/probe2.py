import urllib.request, re, io, sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    return urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
h=fetch('https://t.pia.jp/pia/event/event.do?eventCd=2606479')
# split by ticketSalesCard blocks
cards=re.split(r'(?=ticketSalesCard-2024"[ >])',h)
print('card片数:',len(cards))
# show one full card region (find a card with status)
m=re.search(r'ticketSalesCard-2024".*?(?=ticketSalesCard-2024"|</body)',h,re.S)
if m:
    blk=m.group(0)[:1500]
    print(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','｜',blk))[:900])
