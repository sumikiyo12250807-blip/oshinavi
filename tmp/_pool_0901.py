# -*- coding: utf-8 -*-
import re, json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
src = open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\]);\n', src, re.S)
ev = json.loads(m.group(1))
print('total', len(ev), 'slots', sum(len(e.get('tickets',[])) for e in ev))
new = [e for e in ev if e.get('genre')=='new']
print('pool', len(new))
for e in new:
    u = (e.get('links') or {})
    url = e.get('url') or ''
    src_v = 'e+' if 'eplus.jp' in json.dumps(e, ensure_ascii=False) else 'pia'
    print(e['id'], src_v, e.get('_genre',''), '|', e.get('artist','')[:40], '|', e.get('date',''), '|', len(e.get('tickets',[])),'枠')
