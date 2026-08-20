# -*- coding: utf-8 -*-
"""7/11 期限切れ救済3件（隠れ枠でないがまだ買える枠あり）をぴあ再パースで変換。
  id=1245 ≒JOY（一般発売 7/11 17:00まで販売中）
  id=1870 学生ミュージカルガチバトル（本日14:00一般発売開始）
  id=2148 可憐なアイボリー（当日引換券 7/11 18:00まで）
heal --apply の後に実行すること（最新 index.html を読む）。tickets のみ置換。
"""
import re, json, sys, datetime
sys.path.insert(0, 'tools')
sys.stdout.reconfigure(encoding='utf-8')
from build_pia_entries import build

RESCUE = {
    1245: 'https://t.pia.jp/pia/event/event.do?eventCd=2624630',
    1870: 'https://t.pia.jp/pia/event/event.do?eventCd=2624020',
    2148: 'https://t.pia.jp/pia/event/event.do?eventCd=2613855',
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

ok = []
for i, url in RESCUE.items():
    ev = byid.get(i)
    if not ev:
        print(f'{i} NOT FOUND'); continue
    ne = build({'newid': i, 'artist': ev.get('artist', ''), 'urls': [url]})
    if ne is None:
        print(f'{i} {ev.get("artist","")} → 買える枠ゼロ(削除候補)'); continue
    ev['tickets'] = ne['tickets']
    ok.append(i)
    print(f'{i} {ev.get("artist","")} → convert {len(ne["tickets"])}枠')

bak = f'index.html.bak_{datetime.date.today():%m%d}_rescue'
open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print(f'=== {len(ok)}件救済 (backup {bak}) ===')
