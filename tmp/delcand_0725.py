import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

IDS = [166, 1269, 3068, 3071, 454, 1130, 1328, 1749, 2109, 2184, 2578, 2751, 3106, 299, 2331]

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = {e['id']: e for e in json.loads(m.group(2))}

for i in IDS:
    e = EV.get(i)
    if not e:
        print(f'id={i} 見つからない')
        continue
    links = e.get('links') or {}
    urls = []
    for k in ('pia', 'eplus', 'rakuten', 'official'):
        u = links.get(k)
        if u:
            urls.append((k, u))
    for t in e.get('tickets', []):
        u = t.get('url')
        if u and all(u != x[1] for x in urls):
            urls.append(('ticket', u))
    print(f"id={i} | {e.get('name')} | 公演日={e.get('date')} | genre={e.get('genre')}")
    for k, u in urls:
        print(f"    {k}: {u}")
