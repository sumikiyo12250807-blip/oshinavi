import urllib.request, re, io, sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    return urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
h=fetch('https://t.pia.jp/pia/event/event.do?eventCd=2606479')
# window around first status, wide
i=h.find('ticketSalesCard-2024__status')
print(h[i-700:i+600])
