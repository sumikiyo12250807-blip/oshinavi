# -*- coding: utf-8 -*-
"""id5717 一青窈（宮崎12/4・鹿児島12/5）に、ローチケの締切違いの枠を足す。

■ いまの登録
  先行（宮崎 12/4公演）9/4 11:00発売 〜9/13
  先行（鹿児島 12/5公演）9/4 11:00発売 〜9/13
＝**両方とも締切が9/13**で、9/14以降に始まる枠を1つも持っていない。

■ ローチケの実ページ（2026-09-10・実ブラウザ）
  都城市総合文化ホール（宮崎）12/4 と 宝山ホール（鹿児島）12/5 に、それぞれ3枠：
   ① 抽選プレリク 受付中 9/4 12:00〜9/13 23:59      … 登録済みの先行と**同じ締切**＝足さない
   ② 抽選プレリク 受付前 9/16 12:00〜9/23 23:59     … 🆕足す
   ③ 先着一般発売 発売前 9/26 10:00〜12/3 23:59     … 🆕足す

🚨突き合わせは券種名でなく「県・公演日・締切」で見る
（[[feedback_capture_all_deadlines_on_add]]）。①は締切が同じなので二重にしない。
"""
import io
import json
import re
import sys
from urllib.parse import quote

sys.stdout.reconfigure(encoding='utf-8')
NAME = '一青窈'


def lt(pfkey, mthd, sn, venuecd):
    return ('https://l-tike.com/order/?gLcode=81842&gPfKey=' + pfkey
            + '&gEntryMthd=' + mthd + '&gScheduleNo=' + sn
            + '&gCarrierCd=08&gPfName=' + quote(NAME) + '&gBaseVenueCd=' + venuecd)


MIYAZAKI = '20260810000002269251'
KAGOSHIMA = '20260810000002269252'

SLOTS = [
    {"type": "抽選プレリク2次（宮崎 12/4公演）9/16 12:00発売",
     "startDate": "2026-09-16", "date": "2026-09-16",
     "url": lt(MIYAZAKI, '03', '2', '80632')},
    {"type": "抽選プレリク2次（鹿児島 12/5公演）9/16 12:00発売",
     "startDate": "2026-09-16", "date": "2026-09-16",
     "url": lt(KAGOSHIMA, '03', '2', '88296')},
    {"type": "一般発売（宮崎 12/4公演）9/26 10:00発売",
     "startDate": "2026-09-26", "date": "2026-09-26",
     "url": lt(MIYAZAKI, '01', '1', '80632')},
    {"type": "一般発売（鹿児島 12/5公演）9/26 10:00発売",
     "startDate": "2026-09-26", "date": "2026-09-26",
     "url": lt(KAGOSHIMA, '01', '1', '88296')},
]

src = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

target = None
for e in events:
    if e['id'] == 5717:
        target = e
        break
if target is None:
    print('!! id5717 が無い')
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
