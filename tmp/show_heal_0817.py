# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout.reconfigure(encoding='utf-8')
d = json.load(io.open('tmp/heal_ids.json', encoding='utf-8'))
print(type(d))
if isinstance(d, list):
    for it in d:
        print('---', it.get('id'), it.get('name', ''))
        for t in it.get('tickets', []):
            print('   ', t.get('type'), '| date=', t.get('date'), '| start=', t.get('startDate'))
elif isinstance(d, dict):
    for k, v in d.items():
        print('---', k)
        tk = v.get('tickets') if isinstance(v, dict) else v
        for t in (tk or []):
            print('   ', t.get('type'), '| date=', t.get('date'), '| start=', t.get('startDate'))
