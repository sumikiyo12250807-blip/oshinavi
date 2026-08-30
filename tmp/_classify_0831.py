import json,re,sys,unicodedata,datetime
sys.stdout.reconfigure(encoding='utf-8')
TODAY=datetime.date(2026,8,31)
d=json.load(open('tmp/presale_sweep_0831.json',encoding='utf-8'))
miss=d['missing']
s=open('index.html',encoding='utf-8').read()
ev=json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n',s,re.S).group(1))
def norm(x):
    x=unicodedata.normalize('NFKC',x or '')
    return re.sub(r'[\s　・･/／「」『』【】（）()\[\]~〜\-–—!！?？,、。.＆&]','',x).lower()
names=[(e['id'],e.get('artist',''),norm(e.get('artist',''))) for e in ev if e.get('artist')]
def rls(it):
    r=it.get('rlsdate') or ''
    m=re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})',r)
    return datetime.date(*map(int,m.groups())) if m else None
exact=[];part=[];today=[];unk=[];fresh=[]
for it in miss:
    n=norm(it['artist']); r=rls(it)
    ex=[(i,a) for i,a,na in names if na==n]
    pa=[(i,a) for i,a,na in names if na!=n and len(na)>=5 and len(n)>=5 and (na in n or n in na)]
    if ex: exact.append((it,ex)); continue
    if pa: part.append((it,pa)); continue
    if r is None: unk.append(it); continue
    if r<=TODAY: today.append(it); continue
    fresh.append(it)
print(f'未掲載{len(miss)} → 同名既存(完全){len(exact)} / 部分一致{len(part)} / 本日以前発売{len(today)} / 発売日不明{len(unk)} / 新規{len(fresh)}')
print('\n--- 完全一致（統合行き）---')
for it,ex in exact: print(f"  {it['artist'][:34]:36} {it['perfdate']:14} → 既存 {ex[0][0]} {ex[0][1][:26]}")
print('\n--- 部分一致（要目視）---')
for it,pa in part: print(f"  {it['artist'][:34]:36} {it['perfdate']:14} → 既存 {pa[0][0]} {pa[0][1][:26]}")
print('\n--- 発売日不明 ---')
for it in unk: print(f"  {it['artist'][:40]:42} {it['perfdate']}")
print(f'\n--- 新規 {len(fresh)}件（発売日順）---')
for it in sorted(fresh,key=lambda x:rls(x)):
    print(f"  {rls(it)} 発売 | {it['artist'][:38]:40} | {it['perfdate']:14} | {it['pref']:8} | {it['_lg']}")
json.dump({'fresh':fresh,'exact':[x[0] for x in exact],'part':[x[0] for x in part],'unk':unk,'today':today},
          open('tmp/_cand_0831.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
