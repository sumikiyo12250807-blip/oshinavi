import json,re,urllib.request,html as _html,io,sys,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8')

# next id
src=open('index.html',encoding='utf-8').read()
m=re.search(r'=\s*(\[\s*\{.*?\}\s*\]);',src,re.S)
data=json.loads(m.group(1))
maxid=max(e['id'] for e in data)
existing=set()
for e in data:
    for v in (e.get('links') or {}).values():
        if v and 'Cd=' in str(v):
            mm=re.search(r'event(?:Bundle)?Cd=\w+',v); existing.add(mm.group(0)) if mm else None
    for t in e.get('tickets',[]):
        if t.get('url'):
            mm=re.search(r'event(?:Bundle)?Cd=\w+',t['url']); existing.add(mm.group(0)) if mm else None

dd=json.load(open('tmp/theater_dedup.json',encoding='utf-8'))
batch=dd[100:150]

def fetch(u):
    req=urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'})
    return urllib.request.urlopen(req,timeout=30).read().decode('utf-8','replace')
def txt(s): return _html.unescape(re.sub(r'\s+',' ',re.sub(r'<[^>]+>','',s or ''))).strip()
def parse(h):
    rows=[]
    for it in re.split(r'(?=<li class="ticketSalesList-2024__item)',h):
        if 'ticketSalesCard-2024__status' not in it: continue
        g=lambda p,fl=re.S: (re.search(p,it,fl).group(1) if re.search(p,it,fl) else '')
        title=txt(g(r'__title">(.*?)</p>')); place=txt(g(r'__place"[^>]*>(.*?)</span>'))
        region=txt(g(r'__region">(.*?)</span>')); dts=re.findall(r'datetime="(\d{4}-\d{2}-\d{2})',it); perf=dts[0] if dts else ''; pend=dts[-1] if dts else ''
        stat=re.search(r'__status (is-\w+)">(.*?)(?:<br|</p>)',it,re.S)
        stt=txt(stat.group(2)) if stat else ''
        sd=txt(g(r'__status[^>]*>.*?<br>\s*<span[^>]*>(.*?)</span>'))
        url=g(r'href="(https://t\.pia\.jp/pia/ticketInformation\.do\?[^"]+)"')
        if re.search(r'(販売期間中|受付中)',stt): state='受付中'
        elif '発売前' in stt: state='発売前'
        else: state='受付終了'
        rows.append({'perfdate':perf,'perf_end':pend,'venue':place,'pref':region,'title':title,'state':state,'when':sd,'url':url})
    # dedup
    seen=set();u=[]
    for r in rows:
        k=(r['perfdate'],r.get('perf_end'),r['venue'],r['title'],r['state'],r['when'])
        if k in seen:continue
        seen.add(k);u.append(r)
    return u

out=[]
nid=maxid
for o in batch:
    urls=o['urls']
    allrows=[]
    for u in urls:
        try:
            allrows+=parse(fetch(u))
            time.sleep(0.3)
        except Exception as ex:
            allrows.append({'error':str(ex),'url':u})
    buy=[r for r in allrows if r.get('state') in ('受付中','発売前')]
    # dedup across urls
    seen=set();bu=[]
    for r in buy:
        k=(r['perfdate'],r.get('perf_end'),r['venue'],r['title'],r['state'])
        if k in seen:continue
        seen.add(k);bu.append(r)
    nid+=1
    out.append({'newid':nid,'artist':o['artist'],'buyable':bu,'nbuy':len(bu)})

json.dump(out,open('tmp/parsed50.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('候補',len(batch),'件 / id',out[0]['newid'],'-',out[-1]['newid'])
print('買える枠ゼロ(skip候補):',[o['newid'] for o in out if o['nbuy']==0])
print('買える枠あり:',sum(1 for o in out if o['nbuy']>0),'件')
