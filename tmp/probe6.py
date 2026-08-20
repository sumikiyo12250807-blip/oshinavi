import urllib.request, re, io, sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    return urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
h=fetch('https://t.pia.jp/pia/event/event.do?eventCd=2606479')
i=h.find('ticketSalesList-2024__item')
seg=h[i:i+2600]
# show date-ish fields
for m in re.finditer(r'(__date[^>]*>[^<]*|datetime="[^"]*"|__performance[^>]*>[^<]*|公演日[^<]*|\d{4}/\d{1,2}/\d{1,2}[^<]*)',seg):
    print(repr(m.group(0))[:120])
