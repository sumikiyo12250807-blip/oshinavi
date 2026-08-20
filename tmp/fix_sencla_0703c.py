# -*- coding: utf-8 -*-
"""仙台クラシックフェス1947-1949: buildが同一バッジ8枠を重複生成→ユニーク1枠に集約。
ぴあ買える1枠と一致させる。tickets の (type,startDate,date,url) が同じものは1つに。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
IDS = {1947, 1948, 1949}
for e in EVENTS:
    if e.get('id') in IDS:
        seen, uniq = set(), []
        for t in e.get('tickets', []):
            k = (t.get('type'), t.get('startDate'), t.get('date'), t.get('url'))
            if k in seen: continue
            seen.add(k); uniq.append(t)
        print(f"id={e['id']} tickets {len(e['tickets'])}->{len(uniq)}")
        e['tickets'] = uniq
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html.bak_0703c_fixsencla', 'w', encoding='utf-8').write(h)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("written")
