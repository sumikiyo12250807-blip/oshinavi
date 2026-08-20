# -*- coding: utf-8 -*-
"""id3100 ナオト・インティライミ（e+のみ＝機械照合外）。
一般発売は両公演とも締切済みだが、実ページに当日引換受付が生きている。
  8/1公演 当日引換: 2026/7/30 10:00 〜 2026/7/31 23:59（受付中）
  8/2公演 当日引換: 2026/7/31 10:00 〜 2026/8/1 23:59（本日10:00受付開始）
期限切れの一般発売2枠を落として、この2枠に差し替える。"""
import re, json, datetime, sys
sys.stdout.reconfigure(encoding='utf-8')

NEW = [
    {"type": "当日引換受付（大阪府 8/1公演）〜7/31 23:59",
     "date": "2026-07-31",
     "url": "https://eplus.jp/sf/detail/0144700001-P0030299P021002"},
    {"type": "当日引換受付（大阪府 8/2公演）7/31 10:00発売",
     "date": "2026-08-01",
     "startDate": "2026-07-31",
     "url": "https://eplus.jp/sf/detail/0144700001-P0030299P021001"},
]

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
E = json.loads(m.group(2))

hit = 0
for e in E:
    if e['id'] != 3100:
        continue
    print('before:', json.dumps(e['tickets'], ensure_ascii=False))
    e['tickets'] = NEW
    print('after :', json.dumps(e['tickets'], ensure_ascii=False))
    hit += 1

if hit != 1:
    print('!! 対象が %d 件。中止' % hit); sys.exit(1)

bak = 'index.html.bak_%s_fix3100' % datetime.date.today().strftime('%m%d')
open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(E, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print('=== 適用 (backup: %s) ===' % bak)
