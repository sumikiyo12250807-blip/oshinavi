# -*- coding: utf-8 -*-
"""2738 プロレスリングFREEDOMS を「受付中の4興行」で作り直す（ユーザー指示「1 登録して」2026-08-21）。

削除候補に挙がったが、独立検証で **ぴあに受付中/発売前の別興行が4本あって全部未登録**と分かった。
消すとサイトからFREEDOMSが丸ごと消えて、売っている4公演が載らなくなる
（[[feedback_harvest_name_dedup_blindspot]]の型）。→ 消さずに中身を入れ替える。

  9/6(日)  横浜武道館                  https://t.pia.jp/pia/event/event.do?eventCd=2603690
  9/13(日) TOKYO SQUARE in Itabashi   https://t.pia.jp/pia/event/event.do?eventCd=2629046
  9/25(金) 新木場1st RING             https://t.pia.jp/pia/event/event.do?eventCd=2630387
  10/16(金) 新木場1st RING            https://t.pia.jp/pia/event/event.do?eventCd=2631311

古い枠（8/20後楽園ホール・公演終了済）は置き換える。
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

b = json.load(io.open('tmp/built_2738.json', encoding='utf-8'))[0]
assert len(b['tickets']) == 4, len(b['tickets'])

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
n = 0
for e in EVENTS:
    if e['id'] != 2738:
        continue
    print('before: 枠%d / date=%s / venue=%s / genre=%s' % (
        len(e.get('tickets') or []), e.get('date'), e.get('venue'), e.get('genre')))
    e['tickets'] = b['tickets']
    e['date'] = b['date']
    e['dateLabel'] = b['dateLabel']
    e['venue'] = b['venue']
    e['prefecture'] = b['prefecture']
    e['links'] = dict(e.get('links') or {}, pia='https://t.pia.jp/pia/event/event.do?eventCd=2603690')
    e['verifiedAt'] = '2026-08-21'
    print('after : 枠%d / date=%s / venue=%s' % (len(e['tickets']), e['date'], e['venue']))
    for t in e['tickets']:
        print('   -', t['type'], '|', t.get('date'))
    n += 1

assert n == 1
shutil.copyfile('index.html', 'index.html.bak_0821_freedoms')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('=== 更新 ===')
