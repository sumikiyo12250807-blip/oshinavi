# -*- coding: utf-8 -*-
import json,datetime,collections,re,io,sys
sys.stdout.reconfigure(encoding='utf-8')
d=json.load(open('tmp/presale_sweep_0827.json',encoding='utf-8'))
ms=d['missing']
T=datetime.date(2026,8,27)
o=io.open('tmp/sweep_summary_0827.txt','w',encoding='utf-8')
def pd(s):
    m=re.match(r'(\d{4})/(\d{1,2})/(\d{1,2})',s or '')
    return datetime.date(int(m.group(1)),int(m.group(2)),int(m.group(3))) if m else None
c=collections.Counter(); far=[]
for it in ms:
    if it.get('rlsdate')=='TODAY': c['本日発売']+=1; continue
    dt=pd(it.get('rlsdate',''))
    if not dt: c['発売日不明']+=1; continue
    n=(dt-T).days
    if n<=0: c['発売日が今日以前']+=1
    elif n<=30: c['30日以内に発売']+=1
    else: c['31日より先に発売']+=1; far.append((dt,it))
o.write('未掲載 %d件（URL単位）\n'%len(ms))
for k,v in c.most_common(): o.write('  %-18s %4d\n'%(k,v))
o.write('\n=== 今まで一度も拾えなかった「31日より先に発売」 上位25 ===\n')
for dt,it in sorted(far,key=lambda x:x[0])[:25]:
    o.write('  発売%s (+%3d日)  %-30s %-24s %s\n'%(dt,(dt-T).days,it['artist'][:30],(it.get('perfdate') or '')[:24],it['url']))
o.write('\nジャンル別: %s\n'%dict(collections.Counter(it['_lg'] for it in ms)))
o.close()
print('ok', len(ms), len(far))
