import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
IDS = [1350, 1357, 1695, 2082, 2129, 2779, 2929]
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = {e['id']: e for e in json.loads(m.group(2))}
for i in IDS:
    e = EV.get(i)
    if not e:
        print(i, '見つからない'); continue
    links = e.get('links') or {}
    print('id=%s | %s | 公演日=%s | genre=%s' % (i, e.get('name'), e.get('date'), e.get('genre')))
    for k in ('pia', 'eplus', 'rakuten', 'official'):
        if links.get(k):
            print('    %s: %s' % (k, links[k]))
    for t in e.get('tickets', []):
        if t.get('url'):
            print('    ticket: %s' % t['url'])
