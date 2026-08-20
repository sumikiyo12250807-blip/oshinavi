# -*- coding: utf-8 -*-
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}
for i in [2202, 2212, 2246, 2221]:
    print(i, byid[i]['artist'][:30], '|', byid[i]['links'].get('pia'))
