# -*- coding: utf-8 -*-
"""明日(8/29)発売の枠を機械抽出する。"""
import json,re,io,sys,collections
sys.stdout.reconfigure(encoding='utf-8')
TOM='2026-08-30'
s=open('index.html',encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',s,re.S)
EV=json.loads(m.group(2))
rows=[]
for e in EV:
    if e.get('genre')=='new': continue          # 新着プールは振り分け前なので出さない
    if (e.get('date') or '')<TOM: continue
    for t in e.get('tickets',[]):
        if t.get('soldout'): continue
        if t.get('startDate')==TOM:
            rows.append((e['id'],e.get('artist',''),e.get('genre',''),t.get('type',''),e.get('prefecture',''),e.get('date','')))
o=io.open('tmp/x_cand_0830.md','w',encoding='utf-8')
o.write('# 明日8/29に発売する枠 %d件\n\n'%len(rows))
g=collections.Counter(r[2] for r in rows)
o.write('ジャンル別: %s\n\n'%dict(g.most_common()))
for r in sorted(rows,key=lambda x:(x[2],x[1])):
    o.write('- [%s] id=%d %s ｜ %s ｜ %s ｜ 公演〜%s\n'%(r[2],r[0],r[1],r[3],r[4],r[5]))
o.close()
print('明日発売の枠',len(rows),'件 / エントリ',len(set(r[0] for r in rows)))
print(dict(g.most_common()))
