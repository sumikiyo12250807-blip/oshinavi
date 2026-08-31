# -*- coding: utf-8 -*-
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', src, re.S).group(1))
pool = [e for e in ev if e.get('genre')=='new' and (e.get('links') or {}).get('eplus')]
PREF = re.compile(r'（([^（）]*?[都道府県])\s')
DAY  = re.compile(r'(\d{1,2})/(\d{1,2})')
bad=[]
for e in pool:
    prefs=set(); days=[]
    for t in e.get('tickets',[]):
        ty=t.get('type','')
        m=PREF.search(ty)
        if m: prefs.add(m.group(1))
        seg=ty.split('（',1)[-1]
        for mo,dy in DAY.findall(seg):
            mo,dy=int(mo),int(dy)
            y=2026 if mo>=9 else 2027
            days.append(datetime.date(y,mo,dy))
    maxd=max(days).isoformat() if days else ''
    venues = e.get('venue','')
    nven = venues.count('／')+1 if '（' in venues else 1
    issues=[]
    if maxd and e.get('date')!=maxd: issues.append(f"千秋楽 date={e.get('date')} / 枠の最終公演={maxd}")
    if len(prefs)>nven: issues.append(f"県{len(prefs)}種({'・'.join(sorted(prefs))}) > 会場{nven}件")
    if e.get('prefecture')=='全国': issues.append("prefecture=全国")
    if issues:
        bad.append((e['id'], e.get('artist',''), issues, e.get('dateLabel',''), venues))
print(f"e+プール {len(pool)}件 / 指摘 {len(bad)}件")
for i,(eid,a,iss,dl,v) in enumerate(bad,1):
    print(f"\n{i}. id={eid} {a}")
    print(f"   dateLabel: {dl}")
    print(f"   venue    : {v}")
    for x in iss: print(f"   ⚠ {x}")
