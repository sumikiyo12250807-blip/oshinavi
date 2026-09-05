# -*- coding: utf-8 -*-
import json, io, sys, re
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
EV = json.load(open(r'C:\Users\user\oshinavi\tmp\vfy_all_events_0905.json', encoding='utf-8'))
KEYS = ['Sick2', 'シンギュラリティ', 'DAMILA', 'tzkwym', 'MEME', 'wacci', 'シンガーズハイ', '野村康太',
        '蛾と蝶', 'サーカス', 'おとぎ話', 'SCOOBIE', 'アロージャズ', '東京キューバン', '渡辺真知子',
        '三四郎', 'ティモンディ', 'ぱーてぃーちゃん', 'ARGYROS', 'The Monali', 'BlackHole',
        'メランコリック', 'Planet CHILD', '獅子王', '二万電圧', 'F.A.D']
TARGET = {6935,6936,6937,6938,6939,6940,6941,6942,6943,6944,6945,6103,6295,6080,583}
out = []
for k in KEYS:
    hits = []
    for e in EV:
        s = (e.get('artist') or '') + '|' + (e.get('name') or '') + '|' + (e.get('venue') or '')
        if k.lower() in s.lower():
            hits.append('    id=%s%s date=%s artist=%s name=%s venue=%s' % (
                e['id'], '(対象)' if e['id'] in TARGET else '', e.get('date'), e.get('artist'), e.get('name'), (e.get('venue') or '')[:70]))
    out.append('### %s (%d件)' % (k, len(hits)))
    out += hits
io.open(r'C:\Users\user\oshinavi\tmp\vfy_name_0905.txt', 'w', encoding='utf-8').write('\n'.join(out))
print('ok')
