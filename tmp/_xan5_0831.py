import csv,sys,datetime,re
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')
EPOCH=1288834974657
rows=list(csv.DictReader(open('tmp/x_content_0831.csv',encoding='utf-8')))
def n(r,k):
    try: return int(float(r.get(k) or 0))
    except: return 0
use=[]
for r in rows:
    pid=r.get('Post id') or ''
    if not pid.isdigit(): continue
    r['_dt']=datetime.datetime.fromtimestamp(((int(pid)>>22)+EPOCH)/1000,datetime.timezone.utc)+datetime.timedelta(hours=9)
    r['_t']=r.get('Post text') or ''
    use.append(r)
print(f'{len(use)}投稿  {min(r["_dt"] for r in use):%m/%d} 〜 {max(r["_dt"] for r in use):%m/%d}')
print('\n=== 8/29・8/30の投稿（実績）===')
for r in sorted([x for x in use if x['_dt'].date()>=datetime.date(2026,8,29)],key=lambda x:x['_dt']):
    print(f"  {r['_dt']:%m/%d %H:%M} imp{n(r,'Impressions'):5} clk{n(r,'URL Clicks'):3} RT{n(r,'Reposts')} ♥{n(r,'Likes'):2} 詳細{n(r,'Detail Expands'):3} プロフ{n(r,'Profile visits'):3} | {r['_t'][:44].replace(chr(10),' ')}")
print('\n=== 直近7日の合計 ===')
w=[r for r in use if r['_dt'].date()>=datetime.date(2026,8,24)]
imp=sum(n(r,'Impressions') for r in w); clk=sum(n(r,'URL Clicks') for r in w)
print(f"  投稿{len(w)} imp{imp} clk{clk} CTR{clk/imp*100:.2f}% RT{sum(n(r,'Reposts') for r in w)} 新規フォロー{sum(n(r,'New follows') for r in w)}")
