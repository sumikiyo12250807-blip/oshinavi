import csv,sys,datetime,re
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')
rows=list(csv.DictReader(open('tmp/x_content_0828.csv',encoding='utf-8')))
MON={m:k+1 for k,m in enumerate(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'])}
def n(r,k):
    try: return int(float(r.get(k) or 0))
    except: return 0
use=[]
for r in rows:
    m=re.match(r'\w+, (\w+) (\d+), (\d+)',r.get('Date') or '')
    if not m: continue
    r['_d']=datetime.date(int(m.group(3)),MON[m.group(1)],int(m.group(2)))
    r['_t']=(r.get('Post text') or '')
    use.append(r)
# マツケン（clk47）を外す
out=[r for r in use if n(r,'URL Clicks')<40]
print(f'マツケン1本を除外: {len(use)} → {len(out)}投稿')
def head(r):
    first=re.split(r'[。\n]',r['_t'].strip())[0]
    if 'OSHINAVI' in first: return 'OSHINAVIで始まる'
    if re.match(r'^【',first): return '【】で始まる'
    if re.search(r'(明日|今日|\d+/\d+)',first): return '日付で始まる'
    return '気持ち・言い切りで始まる'
def stat(sel,label):
    if not sel: return
    imp=sum(n(r,'Impressions') for r in sel); clk=sum(n(r,'URL Clicks') for r in sel)
    print(f"  {label:22} 投稿{len(sel):3} imp{imp:6} clk{clk:4} CTR{(clk/imp*100 if imp else 0):5.2f}% 1投稿あたり{clk/len(sel):.2f}")
print('\n【冒頭の型・マツケン抜き】')
h=defaultdict(list)
for r in out: h[head(r)].append(r)
for k in sorted(h,key=lambda k:-len(h[k])): stat(h[k],k)
print('\n【RTの有無・マツケン抜き】')
stat([r for r in out if n(r,'Reposts')>0],'RTあり')
stat([r for r in out if n(r,'Reposts')==0],'RTなし')
print('\n【まとめ vs 主役1組・マツケン抜き】')
mat=[r for r in out if ('ぜんぶ出すわ' in r['_t'] or 'これで全部' in r['_t'] or '発売のチケット' in r['_t'])]
stat(mat,'まとめ')
stat([r for r in out if r not in mat],'まとめ以外')
print('\n【インプの分布】')
imps=sorted(n(r,'Impressions') for r in out)
import statistics
print(f"  中央値{statistics.median(imps):.0f} 平均{statistics.mean(imps):.0f} 最大{max(imps)} 最小{min(imps)}")
print(f"  imp>=1000 の投稿数 {sum(1 for x in imps if x>=1000)} / imp<200 {sum(1 for x in imps if x<200)}")
print('\n【クリックが1回でも付いた投稿の割合】')
c=[r for r in out if n(r,'URL Clicks')>0]
print(f"  {len(c)}/{len(out)} = {len(c)/len(out)*100:.0f}%  （残り{len(out)-len(c)}本はクリック0）")
