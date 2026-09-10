# -*- coding: utf-8 -*-
"""id4329 NEE（全国ツアー）に、ローチケで生きている3枠を足す。

■ なぜ
登録の7枠が全部プレリザーブで締切済み＝**画面に出る枠が0**だった
（[[project_big_artist_crosscheck]] の「載っているが枠が足りない」層）。
ぴあ側には枠が無く（reconcile 0枠）、ローチケにだけ生きた受付がある。

■ 実ブラウザで読んだ事実（2026-09-10・ローチケ検索結果）
  11/1(日) BIGCAT（大阪）        抽選プレリク 受付中 9/2 12:00〜9/13 23:59
  11/3(火) BEAT STATION（福岡）  抽選プレリク 受付中 9/4 10:00〜9/14 23:59
  11/14(土) 仙台darwin（宮城）    先着一般発売 発売前 9/19 10:00〜11/2 23:59

🚨枠ごとに lcode も schduleno も rcptypename も違う＝**URLは枠ごとに別**
（[[reference_ltike_machine_unreachable]]／[[feedback_tour_per_ticket_url]]）。
"""
import io
import json
import re
import sys
from urllib.parse import quote

sys.stdout.reconfigure(encoding='utf-8')


def lt(lcode, pfkey, mthd, sn, venuecd, name='NEE'):
    return ('https://l-tike.com/order/?gLcode=' + lcode + '&gPfKey=' + pfkey
            + '&gEntryMthd=' + mthd + '&gScheduleNo=' + sn
            + '&gCarrierCd=08&gPfName=' + quote(name) + '&gBaseVenueCd=' + venuecd)


U_OSAKA = lt('54753', '20260625000002235445', '03', '3', '53037')
U_FUKUOKA = lt('82959', '20260615000002226691', '03', '3', '81668')
U_SENDAI = lt('22703', '20260617000002230326', '02', '1', '26532')

SLOTS = [
    {"type": "抽選プレリク先行（大阪 11/1公演）〜9/13 23:59",
     "date": "2026-09-13", "url": U_OSAKA},
    {"type": "抽選プレリク先行（福岡 11/3公演）〜9/14 23:59",
     "date": "2026-09-14", "url": U_FUKUOKA},
    {"type": "一般発売（宮城 11/14公演）9/19 10:00発売",
     "startDate": "2026-09-19", "date": "2026-09-19", "url": U_SENDAI},
]

src = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

target = None
for e in events:
    if e['id'] == 4329:
        target = e
        break
if target is None:
    print('!! id4329 が無い')
    sys.exit(1)

have = {(t.get('url') or '') for t in target.get('tickets') or []}
added = 0
for s in SLOTS:
    if s['url'] in have:
        print('  すでにある: %s' % s['type'])
        continue
    target.setdefault('tickets', []).append(s)
    print('  足した: %s' % s['type'])
    added += 1

if not added:
    print('足すものが無かった')
    sys.exit(0)

print('  枠数 %d → %d' % (len(target['tickets']) - added, len(target['tickets'])))

out = (src[:m.start()] + m.group(1)
       + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
io.open('index.html', 'w', encoding='utf-8').write(out)
print('書き込み完了')
