# -*- coding: utf-8 -*-
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
EVENTS = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', h, re.S).group(1))
byid = {e['id']: e for e in EVENTS}
for i in [138, 157, 402]:
    e = byid.get(i)
    print("====", i, e.get('artist'))
    print(json.dumps(e.get('links'), ensure_ascii=False, indent=1))
    for t in e.get('tickets', []):
        print("  ticket:", t.get('type'), "| url=", t.get('url'))
