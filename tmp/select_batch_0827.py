# -*- coding: utf-8 -*-
"""未掲載456件から投入候補を選ぶ。
   優先＝①31日より先に発売（今まで一度も拾えなかった側）②ジャンル優先順（音楽→演劇/クラシック/お笑い→その他）
   除外＝発売日不明・本日発売・既存と同名/部分一致"""
import json,re,sys,io,datetime,unicodedata,collections
sys.stdout.reconfigure(encoding='utf-8')
T=datetime.date(2026,8,27)
d=json.load(open('tmp/presale_sweep_0827.json',encoding='utf-8'))
ms=d['missing']

def pd(s):
    m=re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})',s or '')
    return datetime.date(*(int(x) for x in m.groups())) if m else None
def norm(s):
    s=unicodedata.normalize('NFKC',s or '')
    s=re.sub(r'[\s　・･/／「」『』【】（）()\[\]～~ー-]','',s).lower()
    return s

# 既存エントリの名前
h=open('index.html',encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',h,re.S)
EV=json.loads(m.group(2))
names={}
for e in EV:
    for k in ('artist','name'):
        v=e.get(k)
        if v: names.setdefault(norm(v),e['id'])
namelist=[(n,i) for n,i in names.items() if len(n)>=4]

GP={'音楽':0,'演劇':1,'クラシック':1,'イベント':2,'スポーツ':2,'映画':2,'アート':2}
cand=[]; skipped=collections.Counter(); dup=[]
for it in ms:
    r=it.get('rlsdate','')
    if r=='TODAY': skipped['本日発売']+=1; continue
    dt=pd(r)
    if not dt: skipped['発売日不明']+=1; continue
    if (dt-T).days<=0: skipped['発売日が今日以前']+=1; continue
    a=norm(it['artist'])
    if a in names:
        dup.append((it,'完全一致 id%d'%names[a])); skipped['同名既存(完全)']+=1; continue
    hit=next(((n,i) for n,i in namelist if (n in a or a in n)),None)
    if hit:
        dup.append((it,'部分一致 id%d'%hit[1])); skipped['同名既存(部分)']+=1; continue
    it['_rls']=dt.isoformat(); it['_days']=(dt-T).days
    cand.append(it)

cand.sort(key=lambda x:(0 if x['_days']>30 else 1, GP.get(x['_lg'],3), x['_rls']))
json.dump({'cand':cand,'dup':[{'it':a,'why':b} for a,b in dup]},
          open('tmp/batch_cand_0827.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
print('未掲載 %d → 候補 %d件'%(len(ms),len(cand)))
for k,v in skipped.most_common(): print('  除外 %-16s %d'%(k,v))
print()
print('候補の内訳: 31日より先=%d / 30日以内=%d'%(sum(1 for c in cand if c['_days']>30),sum(1 for c in cand if c['_days']<=30)))
print('ジャンル別:',dict(collections.Counter(c['_lg'] for c in cand)))
