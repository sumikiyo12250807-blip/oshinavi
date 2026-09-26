# 朝の削除候補＝公演日(ev.date)が過去・買える枠なし・券種名に今日以降の公演日が無い
import json,re,sys
from datetime import date
sys.path.insert(0,'tools')
from check_expired import extract_events_array, has_live_ticket
T=date(2026,9,26)
evs=extract_events_array('index.html')
keep=[];dele=[]
def perf_dates(t):
    s=t.get('type','')
    out=[]
    for m in re.finditer(r'(R9年 )?(\d{1,2})/(\d{1,2})', s):
        y=2027 if m.group(1) else 2026
        mo,d=int(m.group(2)),int(m.group(3))
        try: out.append(date(y,mo,d))
        except: pass
    return out
for ev in evs:
    try: d=date.fromisoformat(ev.get('date',''))
    except: continue
    if d>=T or ev.get('saleEndUnknown'): continue
    if has_live_ticket(ev,T): continue
    tk=ev.get('tickets') or []
    if any(date.fromisoformat(t['date'])>=T for t in tk if re.match(r'\d{4}-\d\d-\d\d$',t.get('date',''))): continue
    fut=[x for t in tk for x in perf_dates(t) if x>=T]
    # 発売日表記「9/25 10:00発売」の日付は公演日ではない → 公演括弧の中だけ見る
    fut2=[]
    for t in tk:
        for m in re.finditer(r'（[^）]*）', t.get('type','')):
            for x in perf_dates({'type':m.group(0)}):
                if x>=T: fut2.append(x)
    (keep if fut2 else dele).append((ev,fut2))
print('削除候補',len(dele),'／後の公演が券種名にある＝残す',len(keep))
for ev,f in keep: print('KEEP',ev['id'],ev.get('title','')[:40],sorted(set(f))[:3])
json.dump([ev['id'] for ev,_ in dele],open('tmp/x0926/del_ids.json','w'))
