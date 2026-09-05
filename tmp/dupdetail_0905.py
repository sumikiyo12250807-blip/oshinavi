# -*- coding: utf-8 -*-
import json, io, re
hh = io.open('index.html', encoding='utf-8').read()
db = {e['id']: e for e in json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', hh, re.S).group(1))}
ids = [4115, 6194, 5992, 6103, 1218, 4037, 6295, 583, 6080, 3699]
with io.open('tmp/dupdetail_0905.txt', 'w', encoding='utf-8') as f:
    for i in ids:
        e = db.get(i)
        if not e:
            f.write('id%s なし\n\n' % i); continue
        f.write('■ id%s %s ／ %s\n   date=%s venue=%s pref=%s genre=%s\n'
                % (i, e.get('artist'), e.get('name'), e.get('date'), e.get('venue'), e.get('prefecture'), e.get('genre')))
        for t in e.get('tickets', []):
            f.write('    - %s | 締切%s | %s\n' % (t.get('type'), t.get('date'), (t.get('url') or '')[:70]))
        f.write('\n')
print('OK')
