# -*- coding: utf-8 -*-
import io, re, json
hh = io.open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS\s*=\s*(\[.*?\]);', hh, re.S)
db = json.loads(m.group(1))
ids = [int(e['id']) for e in db if str(e.get('id','')).isdigit()]
print('N=%d MAXID=%d' % (len(db), max(ids)))
print('NEWPOOL=%d' % sum(1 for e in db if e.get('genre') == 'new'))
