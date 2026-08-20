# -*- coding: utf-8 -*-
"""2307 DEXCORE が build 落ち。原因=ぴあURLが旧形式 ticket.pia.jp/pia/event.do
（正規は t.pia.jp/pia/event/event.do）。貼り替えて単体再構築→genre:newで投入。"""
import re, json, sys, io
sys.path.insert(0, 'tools')
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from build_pia_entries import build

URL = 'https://t.pia.jp/pia/event/event.do?eventCd=2612233'
idx = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S)
EVENTS = json.loads(m.group(2))
newid = max(e['id'] for e in EVENTS) + 1

ne = build({'newid': newid, 'artist': 'ＤＥＸＣＯＲＥ', 'urls': [URL]})
if ne is None:
    print('買える枠ゼロ→投入しない（売切/終了）'); sys.exit(0)
ne['genre'] = 'new'
print(json.dumps({k: ne[k] for k in ('id','artist','name','venue','prefecture','date')}, ensure_ascii=False))
for t in ne['tickets']:
    print('  ', t.get('startDate'), '->', t.get('date'), '|', t.get('type'))

if '--apply' not in sys.argv:
    print('(DRY)'); sys.exit(0)
EVENTS.append(ne)
out = idx[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + idx[m.end():]
mo = re.search(r'const NEW_ORDER = \[([^\]]*)\];', out)
cur = [x.strip() for x in mo.group(1).split(',') if x.strip()]
cur.append(str(newid))
out = re.sub(r'(const NEW_ORDER = )\[[^\]]*\](;)', r'\g<1>[' + ', '.join(cur) + r']\2', out, count=1)
open('index.html.bak_0710_dexcore','w',encoding='utf-8').write(idx)
open('index.html','w',encoding='utf-8').write(out)
print(f'投入 id={newid} / NEW_ORDER {len(cur)}件')
