# -*- coding: utf-8 -*-
"""昨日投稿の4組(milet/BABYMONSTER/丘みどり/さくら前線)が7/8発売開始だったか検証。"""
import re, json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
keys = ['milet', 'ミレイ', 'BABYMONSTER', 'ＢＡＢＹ', '丘みどり', 'さくら前線']
for e in EVENTS:
    nm = e.get('artist') or ''
    if any(k.lower() in nm.lower() for k in keys):
        print('id=%d %s [%s]' % (e['id'], nm, e.get('genre')))
        print('   dateLabel=%s' % e.get('dateLabel'))
        print('   pia=%s' % e['links'].get('pia'))
        for t in e['tickets']:
            print('    - %s (%s)' % (t['type'], t['date']))
        print()
