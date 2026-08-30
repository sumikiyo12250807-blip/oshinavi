# 新着プール278件と既存エントリの名前かぶりを検出（振り分け前・ツアー分裂の防止）
import json,re,sys,unicodedata
sys.stdout.reconfigure(encoding='utf-8')
s=open('index.html',encoding='utf-8').read()
ev=json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n',s,re.S).group(1))
def norm(x):
    x=unicodedata.normalize('NFKC',x or '')
    return re.sub(r'[\s　・･/／「」『』【】（）()\[\]~〜\-–—!！?？,、。.＆&]','',x).lower()
pool=[e for e in ev if e.get('genre')=='new']
old=[e for e in ev if e.get('genre')!='new']
oldn=[(e['id'],e.get('artist',''),norm(e.get('artist','')),e.get('date',''),(e.get('links') or {}).get('pia')) for e in old]
exact=[];part=[]
for p in pool:
    n=norm(p.get('artist',''))
    if not n: continue
    for i,a,na,d,u in oldn:
        if not na: continue
        if na==n: exact.append((p['id'],p.get('artist',''),i,a,d))
        elif len(na)>=5 and len(n)>=5 and (na in n or n in na): part.append((p['id'],p.get('artist',''),i,a,d))
print('完全一致',len(exact),'件 ／ 部分一致',len(part),'件')
print('--- 完全一致（統合候補）---')
for x in exact: print(f"  新{x[0]} {x[1][:32]:34} ↔ 既存{x[2]} {x[3][:32]} ({x[4]})")
print('--- 部分一致（要目視）---')
for x in part[:40]: print(f"  新{x[0]} {x[1][:32]:34} ↔ 既存{x[2]} {x[3][:32]} ({x[4]})")
json.dump({'exact':exact,'part':part},open('tmp/_pooldup_0831.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
