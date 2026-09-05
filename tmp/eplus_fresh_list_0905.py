# -*- coding: utf-8 -*-
import json, io
d = json.load(io.open('tmp/eplus_fresh_0905.json', encoding='utf-8'))
with io.open('tmp/eplus_fresh_0905.txt', 'w', encoding='utf-8') as f:
    for i, c in enumerate(d, 1):
        f.write('%2d %s | %s | %s %s | %s\n' % (i, c['eid'], c['date'], c['pref'], c['venue'], c['title']))
print('OK %d' % len(d))
