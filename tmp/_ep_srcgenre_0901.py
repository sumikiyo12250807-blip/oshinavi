# -*- coding: utf-8 -*-
import re, json, sys, glob, collections
sys.stdout.reconfigure(encoding='utf-8')
# 候補JSONから eid -> e+のジャンル を作る
eid2g = {}
for p in glob.glob('tmp/*ep*0830*.json')+glob.glob('tmp/*ep*0831*.json')+['tmp/eplus_live_cand.json']:
    try: d=json.load(open(p,encoding='utf-8'))
    except Exception: continue
    if not isinstance(d,list): continue
    for c in d:
        if isinstance(c,dict) and c.get('eid') and c.get('_genre'):
            eid2g.setdefault(c['eid'], set()).add(c['_genre'])
src = open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'const EVENTS = (\[.*?\]);\n', src, re.S).group(1))
pool=[e for e in ev if e.get('genre')=='new' and (e.get('links') or {}).get('eplus')]
miss=[]; cnt=collections.Counter()
for e in pool:
    urls=[(e.get('links') or {}).get('eplus','')]+[t.get('url','') for t in e.get('tickets',[])]
    eids=list(dict.fromkeys(m.group(1) for u in urls for m in [re.search(r'/sf/detail/(\d+)',u or '')] if m))
    gs=set()
    for x in eids: gs |= eid2g.get(x,set())
    if gs: cnt['|'.join(sorted(gs))]+=1
    else: miss.append(e['id'])
    print(f"{e['id']}  {'/'.join(sorted(gs)) or '???':14} | {e.get('artist','')[:38]}")
print('\n集計:', dict(cnt), ' 不明:', miss)
