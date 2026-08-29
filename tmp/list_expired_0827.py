# -*- coding: utf-8 -*-
import json,re,io,sys
s=open('index.html',encoding='utf-8').read()
m=re.search(r'const EVENTS\s*=\s*(\[.*?\]);\s*\n',s,re.S)
ev=json.loads(m.group(1))
today='2026-08-27'
out=io.open('tmp/expired_0827.md','w',encoding='utf-8')
n=0
for e in ev:
    d=e.get('date','')
    if d and d<today:
        n+=1
        L=e.get('links') or {}
        tks=e.get('tickets',[])
        alive=[t for t in tks if (t.get('date') or '')>=today]
        out.write(f"### id={e['id']} {e.get('artist','')} / {e.get('title','')}\n")
        out.write(f"- 公演日: {d} / 会場: {e.get('venue','')} / ジャンル: {e.get('genre','')}\n")
        out.write(f"- links: {json.dumps(L,ensure_ascii=False)}\n")
        out.write(f"- 枠 {len(tks)}件・うち締切が未来の枠 {len(alive)}件\n")
        for t in tks:
            out.write(f"    - [{'ALIVE' if (t.get('date') or '')>=today else 'dead '}] {t.get('type','')} / date={t.get('date')} / start={t.get('startDate')} / soldout={t.get('soldout')} / url={t.get('url','')}\n")
        out.write("\n")
out.write(f"\n合計 {n}件\n")
out.close()
print("wrote tmp/expired_0827.md", n)
