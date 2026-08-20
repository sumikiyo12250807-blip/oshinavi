import urllib.request,re,html as _html,sys,io
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')
url='https://t.pia.jp/pia/event/event.do?eventCd=2606479'
req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
r=urllib.request.urlopen(req,timeout=30)
print('final URL:',r.geturl())
print('status:',r.status)
h=r.read().decode('utf-8','replace')
ti=re.search(r'<title>(.*?)</title>',h,re.S)
print('title:',_html.unescape(re.sub(r'\s+',' ',ti.group(1))).strip() if ti else '?')
# sorry?
print('sorry in url:', 'sorry' in r.geturl())
print('len:',len(h))
