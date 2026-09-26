# -*- coding: utf-8 -*-
"""ぴあが「受付終了」を出している（＝予定枚数終了の表示なし）エントリの、期限切れの枠に
「販売終了」の印を付ける（2026-09-23 昼）。
DELETE_GATE＝「販売終了（期間が終わっただけ）」は消さない＝soldout:true ＋ saleEnded:true ＋ saleEndedSince。
🚨強い主張（売り切れた）はしない＝弱いほう（販売終了）に倒す。mark_soldout が nosold と判定した分だけ。
🚨公演日がまだ未来のエントリだけ。公演が終わったものは翌朝の削除ルートに任せる。
使い方: python mark_ended.py [--apply]
"""
import io
import json
import re
import sys

APPLY = '--apply' in sys.argv
TODAY = '2026-09-26'
SCR = r"C:\Users\user\AppData\Local\Temp\claude\C--Users-user-oshinavi\211b8b3d-6701-4434-8b7f-224ce869b3f9\scratchpad"

ids = {int(x) for x in io.open("tmp/x0926/nosold.txt", encoding="utf-8").read().split() if x.strip()}
text = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'const\s+EVENTS\s*=\s*(\[)', text)
start = m.start(1)
events, end = json.JSONDecoder().raw_decode(text, start)

log = []
n_ev = 0
n_slot = 0
for ev in events:
    if ev.get('id') not in ids:
        continue
    if (ev.get('date') or '') <= TODAY:
        log.append('skip id=%s 公演が今日まで（翌朝の削除ルートに任せる）' % ev.get('id'))
        continue
    is_pia = bool((ev.get('links') or {}).get('pia'))
    hit = 0
    for t in ev.get('tickets') or []:
        if t.get('soldout') or t.get('saleEnded'):
            continue
        if not (is_pia or 'pia.jp' in (t.get('url') or '')):
            continue
        if (t.get('date') or '9999') >= TODAY:
            continue
        t['soldout'] = True
        t['saleEnded'] = True
        t['saleEndedSince'] = TODAY
        hit += 1
    if hit:
        n_ev += 1
        n_slot += hit
        ev['verifiedAt'] = TODAY
        log.append('OK id=%-6s +%d枠 %s' % (ev.get('id'), hit, (ev.get('name') or '')[:32]))

log.append('--- %d件 %d枠に「販売終了」の印 ---' % (n_ev, n_slot))
io.open('tmp/mark_ended_report.txt', 'w', encoding='utf-8').write('\n'.join(log) + '\n')
sys.stdout.write('done %d entries %d slots\n' % (n_ev, n_slot))
if not APPLY:
    sys.stdout.write('(--apply de write)\n')
    raise SystemExit(0)
body = json.dumps(events, ensure_ascii=False, indent=2).replace('\r\n', '\n').replace('\n', '\r\n')
data = (text[:start] + body + text[end:]).encode('utf-8')
if data.count(b'\r\n') != data.count(b'\n'):
    sys.stdout.write('ABORT: CRLF broken\n')
    raise SystemExit(1)
io.open('index.html', 'wb').write(data)
sys.stdout.write('written (crlf %d)\n' % data.count(b'\r\n'))
