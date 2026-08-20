# -*- coding: utf-8 -*-
"""要目視4件と、同名の既存エントリの中身を並べて出す。"""
import io
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDS = [3696, 3699, 3663, 3719, 3657, 3723]
h = io.open(os.path.join(ROOT, 'index.html'), encoding='utf-8', newline='').read()
byid = {e['id']: e for e in json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))}
out = []
for i in IDS:
    e = byid[i]
    out.append('id=%d | genre=%s _genre=%s _piaSub=%s' % (i, e.get('genre'), e.get('_genre'), e.get('_piaSub')))
    out.append('   name   : %s' % e.get('name'))
    out.append('   date   : %s / %s' % (e.get('date'), e.get('dateLabel')))
    out.append('   venue  : %s (%s)' % (e.get('venue'), e.get('prefecture')))
    out.append('   pia    : %s' % (e.get('links') or {}).get('pia'))
    for t in e.get('tickets') or []:
        out.append('   枠     : %s | date=%s' % (t.get('type'), t.get('date')))
    out.append('')
io.open(os.path.join(ROOT, 'tmp', 'show4_0804.txt'), 'w', encoding='utf-8').write('\n'.join(out) + '\n')
print('wrote tmp/show4_0804.txt')
