# -*- coding: utf-8 -*-
"""新着50件(2605-2654)の全内容ダンプ（目視点検用）"""
import io, json, re

s = io.open('index.html', encoding='utf-8').read()
m = re.search(r'const EVENTS = (\[.*?\n\]);', s, re.S)
ev = json.loads(m.group(1))
new = [e for e in ev if 2605 <= e['id'] <= 2654]

with io.open('tmp/dump_0714.txt', 'w', encoding='utf-8') as f:
    for e in new:
        f.write('--- id=%d [_genre=%s / _piaSub=%s]\n' % (
            e['id'], e.get('_genre'), e.get('_piaSub')))
        f.write('  name  : %s\n' % e.get('name'))
        f.write('  artist: %s\n' % e.get('artist'))
        f.write('  venue : %s (%s)\n' % (e.get('venue'), e.get('prefecture')))
        f.write('  date  : %s | %s\n' % (e.get('date'), e.get('dateLabel')))
        for t in e.get('tickets') or []:
            f.write('    - %s | date=%s start=%s\n' % (
                t.get('type'), t.get('date'), t.get('startDate')))
        links = e.get('links') or {}
        f.write('  pia   : %s\n' % links.get('pia'))
        other = [k for k in ('rakuten', 'lawson', 'eplus') if links.get(k)]
        if other:
            f.write('  other : %s\n' % other)
print('done')
