# -*- coding: utf-8 -*-
import json, io
d = json.load(io.open('tmp/eplus_built.json', encoding='utf-8'))
with io.open('tmp/view_built_0905b.txt', 'w', encoding='utf-8') as f:
    for e in d:
        f.write('■ id%s [%s] artist=%s\n   name=%s\n   date=%s pref=%s venue=%s dateLabel=%s\n'
                % (e.get('id'), e.get('genre'), e.get('artist'), e.get('name'), e.get('date'),
                   e.get('pref'), e.get('venue'), e.get('dateLabel')))
        for t in e.get('tickets', []):
            f.write('    - %s | %s | %s | %s\n' % (t.get('type'), t.get('startDate'), t.get('date'), t.get('url','')[:80]))
        f.write('\n')
print('OK', len(d))
