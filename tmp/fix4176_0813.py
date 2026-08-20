# -*- coding: utf-8 -*-
"""id4176 のURLを機械抽出して cand を作る"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'tools'))
from check_expired import extract_events_array
sys.stdout.reconfigure(encoding='utf-8')

e = [x for x in extract_events_array('index.html') if x['id'] == 4176][0]
urls = []
lk = e.get('links') or {}
if lk.get('pia'):
    urls.append(lk['pia'])
for t in e.get('tickets') or []:
    if t.get('url') and t['url'] not in urls:
        urls.append(t['url'])
print('name=%s' % e.get('name'))
print('genre=%s _genre=%s' % (e.get('genre'), e.get('_genre')))
print('urls=%s' % urls)
cand = [{'newid': 4176, 'artist': e.get('artist'), 'urls': urls}]
json.dump(cand, open('tmp/cand_4176.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('wrote tmp/cand_4176.json')
