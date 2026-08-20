# -*- coding: utf-8 -*-
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
from check_expired import extract_events_array
sys.stdout.reconfigure(encoding='utf-8')

for e in extract_events_array('index.html'):
    if 'ボイスシネマ' in (e.get('name') or '') or '口演' in (e.get('name') or ''):
        print('id=%d genre=%s extra=%s _genre=%s _piaSub=%s' % (
            e['id'], e.get('genre'), e.get('extraGenres'), e.get('_genre'), e.get('_piaSub')))
        print('  name=%s' % e.get('name'))
        print('  venue=%s date=%s' % (e.get('venue'), e.get('date')))
