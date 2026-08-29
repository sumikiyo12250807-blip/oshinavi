import json,re,os,time,urllib.request
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
D=os.path.dirname(os.path.abspath(__file__))
RAW=os.path.join(D,'raw'); os.makedirs(RAW,exist_ok=True)
def key(u): return re.sub(r'[^A-Za-z0-9]+','_',u.split('pia/')[-1])[:120]
def fetch(u,retry=3):
    p=os.path.join(RAW,key(u)+'.html')
    if os.path.exists(p) and os.path.getsize(p)>2000:
        return open(p,encoding='utf-8',errors='replace').read()
    h=''
    for i in range(retry):
        try:
            r=urllib.request.Request(u,headers=UA)
            h=urllib.request.urlopen(r,timeout=40).read().decode('utf-8','replace')
        except Exception: h=''
        if h and ('アクセスが集中' in h or 'ただいま大変混み合' in h):
            time.sleep(25); h=''; continue
        if h and len(h)>2000:
            open(p,'w',encoding='utf-8').write(h); time.sleep(1.0); return h
        time.sleep(6)
    open(p,'w',encoding='utf-8').write(h or ''); return h or ''
TI=r'href="(https://t\.pia\.jp/pia/ticketInformation\.do\?[^"]+)"'
EV=r'href="(https://t\.pia\.jp/pia/event/event\.do\?eventCd=\d+)"'
data=json.load(open(os.path.join(D,'..','verify_in_a_0829.json'),encoding='utf-8'))
man={}
for row in data:
    i=str(row['id']); pages={}; tis=set()
    frontier=list(row['urls']); seen=set()
    while frontier:
        u=frontier.pop(0)
        if u in seen: continue
        seen.add(u)
        h=fetch(u)
        t=set(re.findall(TI,h)); tis|=t
        pages[u]={'len':len(h),'ti':sorted(t)}
        # child events
        childs=set(re.findall(EV,h))
        for c in re.findall(r'ticketInformation\.do\?eventCd=(\d+)',h):
            childs.add('https://t.pia.jp/pia/event/event.do?eventCd=%s'%c)
        for c in sorted(childs):
            if c not in seen: frontier.append(c)
    for t in sorted(tis): fetch(t)
    man[i]={'pages':pages,'ti':sorted(tis)}
    print(i,'pages',len(pages),'ti',len(tis),flush=True)
json.dump(man,open(os.path.join(D,'manifest.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('DONE')
