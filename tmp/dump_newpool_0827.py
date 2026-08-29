# -*- coding: utf-8 -*-
import json,re,io
s=open('index.html',encoding='utf-8').read()
m=re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n',s,re.S)
ev=json.loads(m.group(1))
new=[e for e in ev if e.get('genre')=='new']
out=io.open('tmp/newpool_0827.md','w',encoding='utf-8')
out.write(f"新着プール {len(new)}件\n\n")
for e in new:
    L=e.get('links') or {}
    out.write(f"### id={e['id']} {e.get('artist','')} / {e.get('title','')}\n")
    out.write(f"- 公演日(千秋楽)={e.get('date')} 県={e.get('prefecture')} 会場={e.get('venue')}\n")
    out.write(f"- _piaGenre={e.get('_piaGenre')} _piaSub={e.get('_piaSub')}\n")
    out.write(f"- pia={L.get('pia')}\n")
    for t in e.get('tickets',[]):
        out.write(f"    - {t.get('type','')} | date={t.get('date')} start={t.get('startDate')} url={t.get('url','')}\n")
    out.write("\n")
out.close()
print("newpool", len(new))
