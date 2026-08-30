import csv,sys,datetime,re
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')
EPOCH=1288834974657
rows=list(csv.DictReader(open('tmp/x_content_0828.csv',encoding='utf-8')))
def n(r,k):
    try: return int(float(r.get(k) or 0))
    except: return 0
use=[]
for r in rows:
    pid=r.get('Post id') or ''
    if not pid.isdigit(): continue
    ms=(int(pid)>>22)+EPOCH
    r['_dt']=datetime.datetime.utcfromtimestamp(ms/1000)+datetime.timedelta(hours=9)  # JST
    r['_t']=r.get('Post text') or ''
    use.append(r)
print(f'{len(use)}投稿  {min(r["_dt"] for r in use):%m/%d %H:%M} 〜 {max(r["_dt"] for r in use):%m/%d %H:%M}')
def stat(sel,label):
    if not sel: return
    imp=sum(n(r,'Impressions') for r in sel); clk=sum(n(r,'URL Clicks') for r in sel)
    print(f"  {label:12} 投稿{len(sel):3} imp{imp:6} 平均imp{imp/len(sel):6.0f} clk{clk:4} CTR{(clk/imp*100 if imp else 0):5.2f}%")
print('\n=== 時間帯べつ ===')
buck=defaultdict(list)
for r in use:
    h=r['_dt'].hour
    b=('06-09時' if 6<=h<10 else '10-13時' if 10<=h<14 else '14-16時' if 14<=h<17 else
       '17-19時' if 17<=h<20 else '20-23時' if 20<=h<24 else '深夜0-5時')
    buck[b].append(r)
for b in ('06-09時','10-13時','14-16時','17-19時','20-23時','深夜0-5時'): stat(buck[b],b)
print('\n=== 曜日べつ ===')
W='月火水木金土日'
wb=defaultdict(list)
for r in use: wb[W[r['_dt'].weekday()]].append(r)
for w in W: stat(wb[w],w+'曜')
print('\n=== 本文の長さべつ ===')
lb=defaultdict(list)
for r in use:
    L=len(r['_t'])
    lb('') if False else lb['〜150字' if L<150 else '150-249字' if L<250 else '250-329字' if L<330 else '330字〜'].append(r)
for k in ('〜150字','150-249字','250-329字','330字〜'): stat(lb[k],k)
