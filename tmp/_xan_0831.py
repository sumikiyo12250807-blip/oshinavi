import csv,sys,datetime,re
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')
rows=list(csv.DictReader(open('tmp/x_content_0828.csv',encoding='utf-8')))
def i(r,k):
    try: return int(float(r.get(k) or 0))
    except: return 0
# 3日以上たった投稿だけで判定（伸びは3〜4日続く）
CUT=datetime.date(2026,8,25)
use=[]
for r in rows:
    d=(r.get('Date') or '')[:10]
    try: dt=datetime.date(*map(int,d.split('-')))
    except: continue
    r['_d']=dt
    if dt<=CUT: use.append(r)
print(f'全{len(rows)}投稿 / 判定に使う（8/25以前）{len(use)}投稿')
tot=lambda k,s=use: sum(i(r,k) for r in s)
print(f"  インプ計 {tot('Impressions')}  URLクリック計 {tot('URL Clicks')}  いいね{tot('Likes')} RT{tot('Reposts')} 新規フォロー{tot('New follows')}")
imp=tot('Impressions'); clk=tot('URL Clicks')
print(f"  平均インプ {imp/len(use):.1f} / CTR {clk/imp*100:.2f}%")
# 上位・下位
use2=[r for r in use if i(r,'Impressions')>=50]
use2.sort(key=lambda r:-(i(r,'URL Clicks')))
print('\n=== リンククリックが多い投稿 上位10 ===')
for r in use2[:10]:
    print(f"  {r['_d']} imp{i(r,'Impressions'):5} clk{i(r,'URL Clicks'):3} RT{i(r,'Reposts')} ♥{i(r,'Likes'):3} | {(r['Post text'] or '')[:52].replace(chr(10),' ')}")
print('\n=== インプが多い投稿 上位10 ===')
use3=sorted(use,key=lambda r:-i(r,'Impressions'))
for r in use3[:10]:
    print(f"  {r['_d']} imp{i(r,'Impressions'):5} clk{i(r,'URL Clicks'):3} RT{i(r,'Reposts')} ♥{i(r,'Likes'):3} | {(r['Post text'] or '')[:52].replace(chr(10),' ')}")
# 日別
by=defaultdict(lambda:[0,0,0])
for r in use:
    b=by[r['_d']]; b[0]+=1; b[1]+=i(r,'Impressions'); b[2]+=i(r,'URL Clicks')
print('\n=== 日別（投稿数 / インプ / クリック）===')
for d in sorted(by)[-18:]:
    n,im,cl=by[d]
    print(f"  {d} 投稿{n:2}  imp{im:5}  clk{cl:3}  CTR{(cl/im*100 if im else 0):5.2f}%")
