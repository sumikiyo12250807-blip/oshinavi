# -*- coding: utf-8 -*-
"""発売前を rlsStatus=0102(先着)＋0202(抽選) で7ジャンル総ざらいし、
   index.html に無いものだけを候補として出す。ページ到達率も必ず出す。"""
import json,re,sys,os,subprocess,time
sys.stdout.reconfigure(encoding='utf-8')
LG={'01':'音楽','02':'演劇','07':'クラシック','06':'イベント','03':'スポーツ','04':'映画','05':'アート'}
FILTERS=['rlsStatus=0102','rlsStatus=0202']

# 既存のぴあコード
s=open('index.html',encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',s,re.S)
EV=json.loads(m.group(2))
have=set()
for e in EV:
    urls=[]
    L=e.get('links') or {}
    if L.get('pia'): urls.append(L['pia'])
    for t in e.get('tickets',[]):
        if t.get('url'): urls.append(t['url'])
    for u in urls:
        have|=set(re.findall(r'event(?:Bundle)?Cd=(\w+)',u))
print('既存のぴあコード %d件' % len(have))

allrows=[]; cov=[]
for lg,name in LG.items():
    for f in FILTERS:
        out='tmp/_ph_%s_%s.json'%(lg,f.split('=')[1])
        logp=out+'.log'
        with open(logp,'w',encoding='utf-8') as lf:
            r=subprocess.run([sys.executable,'tools/presale_harvest.py',lg,out,f],
                             stdout=lf,stderr=subprocess.STDOUT)
        if r.returncode!=0 or not os.path.exists(out):
            print('%s %s ❌失敗'%(name,f)); cov.append((name,f,None,None,None)); continue
        d=json.load(open(out,encoding='utf-8'))
        tot=d.get('total',0); pg=d.get('pages',0); fp=d.get('fetched_pages',0)
        n=len(d.get('new',[]))
        reach = (100.0*fp/pg) if pg else 100.0
        print('%-6s %-16s 総%4d ページ%3d/%3d(%.0f%%) 行%4d'%(name,f,tot,fp,pg,reach,n))
        cov.append((name,f,tot,fp,pg))
        for it in d.get('new',[]):
            it['_lg']=name; it['_filter']=f
            allrows.append(it)
        time.sleep(1.0)

# URL単位で重複を落とす
seen=set(); uniq=[]
for it in allrows:
    if it['url'] in seen: continue
    seen.add(it['url']); uniq.append(it)
# 既存にあるコードを除く
def codes(u): return set(re.findall(r'event(?:Bundle)?Cd=(\w+)',u))
missing=[it for it in uniq if not (codes(it['url']) & have)]
json.dump({'coverage':cov,'rows':uniq,'missing':missing},
          open('tmp/presale_sweep_0827.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
bad=[c for c in cov if c[2] is None or (c[4] and c[3]<c[4])]
print()
print('=== 行(券種)%d → URL重複除き%d → 未掲載%d ==='%(len(allrows),len(uniq),len(missing)))
print('ページ未到達のバケツ: %s'%('無し' if not bad else bad))
