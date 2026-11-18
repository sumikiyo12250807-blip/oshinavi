# -*- coding: utf-8 -*-
import io, json
s = io.open('C:/Users/user/oshinavi/index.html', encoding='utf-8').read()
i = s.index('const EVENTS = ') + 15
E = json.JSONDecoder().raw_decode(s[i:])[0]
o = io.open('C:/Users/user/oshinavi/tmp/x1118/art18/find_ids.txt', 'w', encoding='utf-8')
for k in ('表現力選手権', 'Gal whip', 'Guiano'):
    for e in E:
        if k in (e.get('name') or '') + (e.get('artist') or ''):
            o.write('%s | %s | %s | %s | %s\n' % (k, e['id'], e.get('name'), e.get('genre'), [(t.get('type'), t.get('url')) for t in e.get('tickets', [])][:3]))
o.close()
