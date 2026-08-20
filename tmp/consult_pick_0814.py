# -*- coding: utf-8 -*-
"""人の判断が要る子を洗い出す（未マップsubcat / 会場業態カテゴリ）。"""
import re, json, sys
sys.stdout.reconfigure(encoding='utf-8')
h = open('index.html', encoding='utf-8', newline='').read()
EV = json.loads(re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S).group(2))
TARGET = ('イベント/ショー・ファンイベント', 'イベント/スクール・レジャー',
          'スポーツ/スポーツその他', '音楽/音楽その他')
for e in EV:
    if not (4226 <= e.get('id', 0) <= 4275):
        continue
    if e.get('_piaSub') in TARGET:
        print('id%s  _piaSub=%s  _genre=%s  extra=%s' % (
            e['id'], e.get('_piaSub'), e.get('_genre'), e.get('_extraGenres')))
        print('   name  :', e.get('name'))
        print('   artist:', e.get('artist'))
        print('   venue :', e.get('venue'), '/', e.get('prefecture'))
        print('   date  :', e.get('dateLabel'))
        for t in e.get('tickets') or []:
            print('   枠    :', t.get('type'), '|', t.get('startDate'), '→', t.get('date'))
        print()
