# -*- coding: utf-8 -*-
import json, io
d = json.load(io.open('tmp/inject_all_0905.json', encoding='utf-8'))
with io.open('tmp/peek_injectall_0905.txt', 'w', encoding='utf-8') as f:
    f.write('N=%d\n' % len(d))
    for e in d:
        f.write('id%s %s ／ %s | %s | %s\n' % (e.get('id'), e.get('artist'), e.get('name'), e.get('date'), e.get('venue')))
print('OK', len(d))
