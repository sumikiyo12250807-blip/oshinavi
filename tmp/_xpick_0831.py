# 今夜のX投稿の候補＝「明日(9/1)〜3日後(9/3)に発売開始」の枠を全部出す（2026-08-31の新方針）
import json,re,sys,datetime
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')
s=open('index.html',encoding='utf-8').read()
ev=json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n',s,re.S).group(1))
GL=dict(re.findall(r"['\"]?([A-Za-z0-9_.]+)['\"]?\s*:\s*['\"]([^'\"]+)['\"]",
    re.search(r'const GENRE_LABEL\s*=\s*\{(.*?)\}\s*;',s,re.S).group(1)))
D0=datetime.date(2026,9,1); D3=datetime.date(2026,9,3)
rows=[]
for e in ev:
    if e.get('genre')=='new': continue
    for t in e.get('tickets',[]):
        if t.get('soldout'): continue
        sd=t.get('startDate')
        if not sd: continue
        try: d=datetime.date.fromisoformat(sd)
        except ValueError: continue
        if D0<=d<=D3:
            m=re.search(r'(\d{1,2}):(\d{2})発売',t.get('type',''))
            rows.append({'id':e['id'],'artist':e.get('artist',''),'genre':e.get('genre',''),
                         'g':GL.get(e.get('genre',''),e.get('genre','')),
                         'sd':sd,'time':f"{int(m.group(1)):02d}:{m.group(2)}" if m else '',
                         'type':t.get('type',''),'pref':e.get('prefecture','')})
print(f'9/1〜9/3に発売開始の枠 {len(rows)}件 / エントリ {len({r["id"] for r in rows})}件')
by=defaultdict(list)
for r in rows: by[r['sd']].append(r)
for d in sorted(by): print(f"  {d}: {len(by[d])}枠 / {len({r['id'] for r in by[d]})}組")
print('\n=== ジャンル別 ===')
bg=defaultdict(set)
for r in rows: bg[r['g']].add(r['artist'])
for g,names in sorted(bg.items(),key=lambda x:-len(x[1])):
    print(f"  {g:14} {len(names):3}組")
json.dump(rows,open('tmp/_xcand_0831.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
