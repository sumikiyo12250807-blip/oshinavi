# -*- coding: utf-8 -*-
import io, json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'C:/Users/user/oshinavi/tools')
import tiget_harvest as TH
import build_tiget_entries as BT
S = json.load(io.open('C:/Users/user/oshinavi/tmp/x1117/spot/sample_B.json', encoding='utf-8'))
e = next(x for x in S if x['id'] == 50157)
u = next(t['url'] for t in e['tickets'] if 'tiget' in (t.get('url') or ''))
eid = re.search(r'events/(\d+)', u).group(1)
h = TH.fetch('https://tiget.net/events/' + eid)
d = TH.parse_event(h, eid)
o = io.open('C:/Users/user/oshinavi/tmp/x1117/spot/tiget50157.txt', 'w', encoding='utf-8')
o.write(repr({k: (str(v)[:300]) for k, v in d.items()}) + '\n')
o.write('artist_from ' + repr(BT.artist_from(d, d.get('name') or '')) + '\n')
for m in re.finditer('MamaCrown', h):
    o.write('\n----\n' + h[max(0, m.start() - 500):m.start() + 120])
