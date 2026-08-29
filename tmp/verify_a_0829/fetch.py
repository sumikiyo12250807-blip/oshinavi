import json,re,os,sys,time,urllib.request,hashlib
UA={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'}
D=os.path.dirname(os.path.abspath(__file__))
RAW=os.path.join(D,'raw'); os.makedirs(RAW,exist_ok=True)
def key(u):
    return re.sub(r'[^A-Za-z0-9]+','_',u.split('pia/')[-1])[:120]
def fetch(u,retry=3):
    p=os.path.join(RAW,key(u)+'.html')
    if os.path.exists(p) and os.path.getsize(p)>2000:
        return open(p,encoding='utf-8',errors='replace').read()
    for i in range(retry):
        try:
            r=urllib.request.Request(u,headers=UA)
            h=urllib.request.urlopen(r,timeout=40).read().decode('utf-8','replace')
        except Exception as e:
            h=''
        if h and ('アクセスが集中' in h or 'ただいま大変混み合' in h):
            time.sleep(20); continue
        if h and len(h)>2000:
            open(p,'w',encoding='utf-8').write(h); time.sleep(1.2); return h
        time.sleep(8)
    open(p,'w',encoding='utf-8').write(h or '')
    return h or ''
def links(h,pat):
    return sorted(set(re.findall(pat,h)))
data=json.load(open(os.path.join(D,'..','verify_in_a_0829.json'),encoding='utf-8'))
manifest={}
for row in data:
    i=row['id']; ent={'urls':row['urls'],'events':{},'bundle_children':[]}
    todo=[]
    for u in row['urls']:
        h=fetch(u)
        if 'BundleCd' in u:
            ch=links(h,r'href="(https://t\.pia\.jp/pia/event/event\.do\?eventCd=\d+)"')
            ent['bundle_children']+=ch
            todo+=ch
            ent['bundle_ok']=bool(h)
        else:
            todo.append(u)
    for u in todo:
        h=fetch(u)
        ti=links(h,r'href="(https://t\.pia\.jp/pia/ticketInformation\.do\?[^"]+)"')
        lot=links(h,r'href="(https://t\.pia\.jp/pia/lot/[^"]+)"')
        ent['events'][u]={'len':len(h),'ti':ti,'lot':lot}
        for t in ti+lot: fetch(t)
    manifest[i]=ent
    print(i,'bundlechildren',len(ent['bundle_children']),'events',len(ent['events']),'ti',sum(len(v['ti'])+len(v['lot']) for v in ent['events'].values()),flush=True)
json.dump(manifest,open(os.path.join(D,'manifest.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=1)
