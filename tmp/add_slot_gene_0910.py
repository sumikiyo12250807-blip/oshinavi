# -*- coding: utf-8 -*-
"""id3568 GENERATIONS from EXILE TRIBE に、ローチケで生きている枠を足す。

■ なぜ
登録は2枠だけ（プレリザーブ6次＝8/23終了／プリセール静岡＝9/13）で、
9/14以降に始まる枠を1つも持っていなかった（[[project_big_artist_crosscheck]]）。

■ 実ブラウザで読んだ事実（2026-09-10・ローチケ検索結果）
  12/22(火) 国立代々木競技場 第一体育館（東京）先着プレリク 発売中 4/17 15:00〜9/16 23:00
  12/11(金) 静岡エコパアリーナ            先着プレリク 発売中 7/1 12:00〜9/16 23:00
  12/11(金) 静岡エコパアリーナ            先着一般発売 発売前 9/19 10:00〜12/2 22:00

⏸ **福岡 11/3 マリンメッセ福岡A館（抽選プレリク 受付中〜9/13）は今回入れない。**
   このエントリの会期は「12/11〜12/22」で、足すと会期・会場・公演日を書き換えることになる。
   ぴあ側のツアー全体を見てから直す（[[feedback_pia_bundle_hides_shows]]／
   [[feedback_show_true_dates_not_sellable_range]]）。
"""
import io
import json
import re
import sys
from urllib.parse import quote

sys.stdout.reconfigure(encoding='utf-8')
NAME = 'ＧＥＮＥＲＡＴＩＯＮＳ　ｆｒｏｍ　ＥＸＩＬＥ　ＴＲＩＢＥ'


def lt(lcode, pfkey, mthd, sn, venuecd):
    return ('https://l-tike.com/order/?gLcode=' + lcode + '&gPfKey=' + pfkey
            + '&gEntryMthd=' + mthd + '&gScheduleNo=' + sn
            + '&gCarrierCd=08&gPfName=' + quote(NAME) + '&gBaseVenueCd=' + venuecd)


SLOTS = [
    {"type": "先着プレリク（東京 12/22公演）〜9/16 23:00",
     "date": "2026-09-16",
     "url": lt('75369', '20260128000002128577', '02', '3', '35016')},
    {"type": "先着プレリク（静岡 12/11公演）〜9/16 23:00",
     "date": "2026-09-16",
     "url": lt('41607', '20251222000002108600', '02', '3', '48228')},
    {"type": "一般発売（静岡 12/11公演）9/19 10:00発売",
     "startDate": "2026-09-19", "date": "2026-09-19",
     "url": lt('41607', '20251222000002108600', '02', '4', '48228')},
]

src = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

target = None
for e in events:
    if e['id'] == 3568:
        target = e
        break
if target is None:
    print('!! id3568 が無い')
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
