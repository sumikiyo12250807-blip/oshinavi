# -*- coding: utf-8 -*-
"""統合用のbuild入力を作る＝既存エントリのぴあURL＋未登録URLをまとめて渡す。"""
import json,re,io,sys
sys.stdout.reconfigure(encoding='utf-8')
todo=json.load(open('tmp/merge_todo_0828.json',encoding='utf-8'))
h=open('index.html',encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',h,re.S)
EV={e['id']:e for e in json.loads(m.group(2))}
def norm(u):
    return u.replace('http://','https://').replace('ticket.pia.jp/pia/event.do','t.pia.jp/pia/event/event.do')
out=[]
for sid,items in todo.items():
    i=int(sid); e=EV.get(i)
    if not e: continue
    urls=[]
    p=(e.get('links') or {}).get('pia')
    if p: urls.append(norm(p))
    for t in e.get('tickets',[]):
        if t.get('url'):
            u=norm(t['url'])
            if u not in urls: urls.append(u)
    for it in items:
        u=norm(it['url'])
        if u not in urls: urls.append(u)
    out.append({'newid':i,'artist':e.get('artist',''),'urls':urls})
out.sort(key=lambda x:-len(x['urls']))
io.open('tmp/merge_in_0828.json','w',encoding='utf-8').write(json.dumps(out,ensure_ascii=False,indent=1))
print('対象 %d件 / URL合計 %d本'%(len(out),sum(len(x['urls']) for x in out)))
