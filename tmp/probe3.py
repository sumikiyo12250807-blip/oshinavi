import urllib.request, re, io, sys
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
    return urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
h=fetch('https://t.pia.jp/pia/event/event.do?eventCd=2606479')
cards=re.findall(r'ticketSalesCard-2024">.*?(?=<li[^>]*ticketSalesCard-2024">|</ul>)',h,re.S)
if not cards:
    # fallback: split
    parts=h.split('ticketSalesCard-2024">')
    cards=parts[1:]
print('cards:',len(cards))
c=cards[0][:2500]
# show with tags as markers but keep date/status text
print(re.sub(r'\s+',' ', re.sub(r'<(/?)(\w+)[^>]*>', r'[\2]', c))[:1400])
