# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
from check_expired import extract_events_array
sys.stdout.reconfigure(encoding='utf-8')

for e in extract_events_array('index.html'):
    if 'Hyogo' in (e.get('name') or '') or 'クリスマス・ジャズ' in (e.get('name') or ''):
        print('=== id=%d genre=%s _genre=%s' % (e['id'], e.get('genre'), e.get('_genre')))
        print('  name   = %s' % e.get('name'))
        print('  artist = %s' % e.get('artist'))
        print('  venue  = %s / pref=%s' % (e.get('venue'), e.get('prefecture')))
        print('  date   = %s / label=%s' % (e.get('date'), e.get('dateLabel')))
        print('  pia    = %s' % (e.get('links') or {}).get('pia'))
        for t in e.get('tickets') or []:
            print('   枠| %s | start=%s end=%s url=%s' % (
                t.get('type'), t.get('startDate'), t.get('date'), t.get('url')))
