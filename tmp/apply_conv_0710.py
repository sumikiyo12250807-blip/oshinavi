# -*- coding: utf-8 -*-
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
built = {o['id']: o for o in json.load(open('tmp/convert_0710.json', encoding='utf-8'))}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
changed = 0
for e in EVENTS:
    o = built.get(e.get('id'))
    if not o or o.get('status') != 'convert': continue
    if not o.get('tickets'):
        print('SKIP empty', e['id']); continue
    e['tickets'] = o['tickets']
    e['date'] = o['date']
    if o.get('venue'): e['venue'] = o['venue']
    if o.get('prefecture'): e['prefecture'] = o['prefecture']
    if o.get('dateLabel'): e['dateLabel'] = o['dateLabel']
    changed += 1
    print(f"  convert id={e['id']} {e.get('artist','')[:24]} tickets={len(o['tickets'])} date={o['date']}")
print(f"=== convert {changed}/{sum(1 for o in built.values() if o.get('status')=='convert')} ===")
if DRY:
    print("(DRY)")
else:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0710_morning_convert','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():])
    print("written (backup: index.html.bak_0710_morning_convert)")
