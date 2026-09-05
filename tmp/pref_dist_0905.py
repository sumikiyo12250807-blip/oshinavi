# -*- coding: utf-8 -*-
import json, io, re, collections
hh = io.open('index.html', encoding='utf-8').read()
db = json.loads(re.search(r'const EVENTS\s*=\s*(\[.*?\]);', hh, re.S).group(1))
c = collections.Counter((e.get('prefecture') or '') for e in db)
long = {k: v for k, v in c.items() if k.endswith(('都', '府', '県'))}
with io.open('tmp/pref_dist_0905.txt', 'w', encoding='utf-8') as f:
    f.write('全%d件 / 「都府県」付き %d種 %d件\n' % (len(db), len(long), sum(long.values())))
    for k, v in sorted(long.items(), key=lambda x: -x[1])[:15]:
        f.write('  %s %d\n' % (k, v))
    f.write('\n上位20（全体）\n')
    for k, v in c.most_common(20):
        f.write('  %r %d\n' % (k, v))
print('OK')
