# -*- coding: utf-8 -*-
import json, io, sys, collections
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
EV = json.load(open(r'C:\Users\user\oshinavi\tmp\vfy_all_events_0905.json', encoding='utf-8'))
c = collections.Counter((e.get('prefecture') or '') for e in EV)
rows = []
for k in ('岡山', '岡山県', '奈良', '奈良県', '愛知', '愛知県', '東京', '東京都', '大阪', '大阪府', '神奈川', '神奈川県', '埼玉', '埼玉県'):
    rows.append('%s : %d' % (k, c.get(k, 0)))
io.open(r'C:\Users\user\oshinavi\tmp\vfy_pref_0905.txt', 'w', encoding='utf-8').write('\n'.join(rows))
print('ok')
