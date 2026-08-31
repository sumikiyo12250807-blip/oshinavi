# -*- coding: utf-8 -*-
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', src, re.S).group(1))
hit=[]
for e in ev:
    for t in e.get('tickets',[]):
        if t.get('soldout'): continue
        sd, d = t.get('startDate'), t.get('date')
        if sd == TODAY and d and d > TODAY and re.search(r'\d{1,2}/\d{1,2}\s+\d{1,2}:\d{2}発売', t.get('type','')):
            hit.append((e['id'], e.get('artist','')[:30], t['type'][:70], sd, d))
print(f"「〆切日に発売時刻」型（startDate=今日 & 締切が未来 & 型が『M/D HH:MM発売』）: {len(hit)}件")
for h in hit: print(' ', h)
