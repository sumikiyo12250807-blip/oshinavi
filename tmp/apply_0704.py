# -*- coding: utf-8 -*-
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv
prop = json.load(open('tmp/convert_0704.json', encoding='utf-8'))
conv = {o['id']: o for o in prop if o['status'] == 'convert'}
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
changed = 0
for e in EVENTS:
    o = conv.get(e.get('id'))
    if not o: continue
    if not o['tickets']:
        print('SKIP empty', e['id']); continue
    print(f"  id={e['id']} {o.get('artist','')[:22]} tickets {len(e.get('tickets',[]))}->{len(o['tickets'])} date->{o['date']}")
    e['tickets'] = o['tickets']; e['date'] = o['date']
    if o.get('venue'): e['venue'] = o['venue']
    if o.get('prefecture'): e['prefecture'] = o['prefecture']
    changed += 1
print(f"=== convert {changed}/{len(conv)} ===")
if DRY: print("(DRY)")
else:
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html.bak_0704_morning_convert','w',encoding='utf-8').write(h)
    open('index.html','w',encoding='utf-8').write(h[:m.start()]+m.group(1)+new_arr+m.group(3)+h[m.end():])
    print("written (backup: index.html.bak_0704_morning_convert)")
