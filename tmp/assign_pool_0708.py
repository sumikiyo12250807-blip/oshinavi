# -*- coding: utf-8 -*-
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
override = {
 2138:'classic', 2139:'fes', 2141:'kpop', 2142:'fes', 2143:'jpop',
 2144:'jpop', 2145:'classic', 2157:'jpop', 2164:'jpop', 2176:'kpop',
 2177:'classic', 2179:'dento', 2180:'classic', 2184:'kpop',
}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
from collections import Counter
tally = Counter(); n=0
for e in EVENTS:
    if e.get('genre') != 'new': continue
    i = e['id']
    g = override.get(i, e.get('_genre'))
    if not g or g=='new':
        print("!! unresolved", i, e.get('_genre')); continue
    e['genre'] = g
    for k in ('_genre','_piaSub','_extraGenres'):
        e.pop(k, None)
    tally[g]+=1; n+=1
print(f"=== assigned {n} 件 ===")
for k,v in sorted(tally.items(), key=lambda x:-x[1]):
    print(f"   {k}: {v}")
# NEW_ORDER clear (pool emptied)
no = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])(;)', h)
newh = h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():]
if no:
    newh = re.sub(r'(const NEW_ORDER = )\[[^\]]*\](;)', r'\1[]\2', newh, count=1)
    print("NEW_ORDER cleared")
if DRY:
    print("(DRY)")
else:
    open('index.html.bak_0708_assign','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(newh)
    print("written (backup: index.html.bak_0708_assign)")
