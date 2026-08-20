# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding='utf-8')
from collections import Counter
d = json.load(open('tmp/heal_stale.json', encoding='utf-8'))
print(Counter(o['status'] for o in d))
print('--- delete(buy zero) ---')
for o in d:
    if o['status'] == 'delete':
        print(o['id'], o.get('artist', ''))
print('--- ERROR / NO_PIA_URL ---')
for o in d:
    if o['status'] in ('ERROR', 'NO_PIA_URL'):
        print(o['id'], o['status'], o.get('artist', ''), o.get('err', ''))
