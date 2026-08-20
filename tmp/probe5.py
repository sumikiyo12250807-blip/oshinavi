import urllib.request, re, io, sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    return urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
h=fetch('https://t.pia.jp/pia/event/event.do?eventCd=2606479')
# find the title/date selectors: dump a card from its <li ...item> start
i=h.find('ticketSalesList-2024__item')
seg=h[i:i+1400]
print(re.sub(r'>\s+<','><',seg))
