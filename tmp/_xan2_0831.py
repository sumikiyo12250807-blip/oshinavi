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

def kind(r):
    t=r['_t']
    if 'ぜんぶ出すわ' in t or 'これで全部' in t or '発売のチケット' in t or 'まとめ' in t: return 'まとめ'
    if t.startswith('OSHINAVIの'): return 'テンプレ型'
    if re.match(r'^【',t): return '【】告知型'
    return '主役1組・語りだし'

def stat(sel,label):
    if not sel: return
    imp=sum(n(r,'Impressions') for r in sel); clk=sum(n(r,'URL Clicks') for r in sel)
    rt=sum(n(r,'Reposts') for r in sel); lk=sum(n(r,'Likes') for r in sel)
    print(f"  {label:16} 投稿{len(sel):3}  imp{imp:6}  clk{clk:4}  CTR{(clk/imp*100 if imp else 0):5.2f}%  RT{rt:3} ♥{lk:3}  1投稿あたりclk{clk/len(sel):.2f}")

print('=== 投稿の型べつ（7/1〜8/28・203投稿）===')
g=defaultdict(list)
for r in use: g[kind(r)].append(r)
for k in ('主役1組・語りだし','テンプレ型','【】告知型','まとめ'):
    stat(g[k],k)

print('\n=== 画像の有無で比べる（本文にpic/画像リンクの痕跡があるか）===')
# CSVからは画像有無が取れないので触れない

print('\n=== RTが付いた投稿とそうでない投稿 ===')
stat([r for r in use if n(r,'Reposts')>0],'RTあり')
stat([r for r in use if n(r,'Reposts')==0],'RTなし')

print('\n=== 冒頭の型（1文目）で比べる ===')
def head(r):
    t=r['_t'].strip()
    first=re.split(r'[。\n]',t)[0]
    if 'OSHINAVI' in first: return 'OSHINAVIで始まる'
    if re.match(r'^【',first): return '【】で始まる'
    if re.search(r'(明日|今日|\d+/\d+)',first): return '日付で始まる'
    return '気持ち・言い切りで始まる'
h=defaultdict(list)
for r in use: h[head(r)].append(r)
for k in sorted(h,key=lambda k:-len(h[k])): stat(h[k],k)

print('\n=== ジャンル語が本文にあるか（K-POP/落語/クラシック等）===')
for kw in ('落語','クラシック','K-POP','ミュージカル','プロレス','アニメ','ジャズ','宝塚'):
    sel=[r for r in use if kw in r['_t']]
    if len(sel)>=4: stat(sel,kw)
