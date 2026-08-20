import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = {e['id']: e for e in json.loads(m.group(2))}

for i in (3173, 3175, 3170, 3214):
    e = EV.get(i)
    if not e:
        continue
    print('id=%s | %s' % (i, e.get('name')))
    print('   artist=%s venue=%s pref=%s date=%s' % (e.get('artist'), e.get('venue'), e.get('prefecture'), e.get('date')))
    print('   pia=%s' % ((e.get('links') or {}).get('pia')))
    for t in e.get('tickets', []):
        print('   枠:', t.get('type'), '|', t.get('dateLabel'))
    print()
