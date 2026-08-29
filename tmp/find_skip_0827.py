# -*- coding: utf-8 -*-
"""同じ締切の枠が複数ある新着＝reconcileが対を確定できず未照合(skip)になった枠を特定する。"""
import json,re,io,sys,collections
sys.stdout.reconfigure(encoding='utf-8')
h=open('index.html',encoding='utf-8',newline='').read()
m=re.search(r'(  const EVENTS = )(\[.*?\])(;)',h,re.S)
EV=[e for e in json.loads(m.group(2)) if 5332<=e['id']<=5431]
o=io.open('tmp/skip_0827.md','w',encoding='utf-8')
n=0
for e in EV:
    c=collections.Counter((t.get('date'),t.get('startDate')) for t in e.get('tickets',[]))
    dupk=[k for k,v in c.items() if v>=2]
    if dupk:
        n+=1
        o.write('### id=%d %s\n- pia=%s\n'%(e['id'],e.get('artist',''),(e.get('links') or {}).get('pia')))
        for t in e.get('tickets',[]):
            mark='🚨' if (t.get('date'),t.get('startDate')) in dupk else '  '
            o.write('  %s %s | date=%s start=%s url=%s\n'%(mark,t.get('type',''),t.get('date'),t.get('startDate'),t.get('url','')))
        o.write('\n')
o.close()
print('同締切の枠を持つエントリ',n)
