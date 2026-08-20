# -*- coding: utf-8 -*-
import io, re, sys, json
sys.stdout.reconfigure(encoding='utf-8')
idx = io.open('index.html', encoding='utf-8').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S).group(2))
IDS = [4436, 4446, 4450, 4477, 4448, 4476, 4455, 4478]
for e in EV:
    if e['id'] not in IDS:
        continue
    print('--- %d %s' % (e['id'], e.get('artist', '')))
    print('    name   :', e.get('name', ''))
    print('    venue  :', e.get('venue', ''), '/', e.get('prefecture', ''), '/ date', e.get('date'))
    print('    links  :', json.dumps(e.get('links') or {}, ensure_ascii=False))
    for t in e.get('tickets') or []:
        print('    枠: %-40s %s〜%s  %s' % (t.get('type', '')[:40], t.get('startDate'), t.get('date'), (t.get('url') or '')[:78]))
