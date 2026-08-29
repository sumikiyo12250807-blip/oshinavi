import sys,re,urllib.parse,urllib.request,time,html as H
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
FILTERS=['','rlsStatus=0101','rlsStatus=0102','rlsStatus=0201','rlsStatus=0202']
def fetch(u):
    for i in range(3):
        try:
            return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=30).read().decode('utf-8','replace')
        except Exception:
            time.sleep(3)
    return ''
out=[]
for kw in sys.argv[1:]:
    found={}
    for f in FILTERS:
        for page in (1,2):
            u='https://t.pia.jp/pia/rlsInfo.do?kw=%s%s&page=%d'%(urllib.parse.quote(kw),('&'+f if f else ''),page)
            h=fetch(u)
            for m in re.finditer(r'<a href="([^"]*event\.do\?event(?:Bundle)?Cd=\w+)"[^>]*>(.*?)</a>',h,re.S):
                url=m.group(1).replace('http://','https://')
                nm=H.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',m.group(2)))).strip()
                found.setdefault(url,nm)
            time.sleep(0.7)
    out.append('== %s'%kw)
    for u,n in sorted(found.items()):
        out.append('   %s  %s'%(u,n))
open('C:/Users/user/oshinavi/tmp/verify_a_0829/kwsearch.txt','a',encoding='utf-8').write('\n'.join(out)+'\n')
print('done',len(out))
