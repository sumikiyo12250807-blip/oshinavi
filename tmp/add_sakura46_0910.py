# -*- coding: utf-8 -*-
"""櫻坂46「15th Single BACKS LIVE!!」を投入する（2026-09-10）。

ユーザー（2026-09-10）＝「大物で、みんなが行きたそうなコンサートはうちにないものがないか探して」
→ ローチケ 9/21-9/27発売の週スキャンで見つけた。**ぴあにも楽天にも無い＝ローチケでしか買えない**
   （ぴあ検索0件・楽天チケット検索0件を実測）。

枠は2つ。**売れ切れた枠も消さずに載せる**（[[feedback_soldout_keep_visible]]）＝
 ①9/5 12:00〜9/16 22:00 … 予定枚数終了
 ②9/22 18:00〜9/30 18:30 … 販売再開（発売前）
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

BASE = ('https://l-tike.com/order/?gLcode=74804'
        '&gPfKey=20260605000002219809%2C20260605000002219808'
        '&gEntryMthd=02&gScheduleNo=SN&gCarrierCd=08'
        '&gPfName=%E6%AB%BB%E5%9D%82%EF%BC%94%EF%BC%96&gBaseVenueCd=34799')
U1, U2 = BASE.replace('SN', '1'), BASE.replace('SN', '2')

NEW = {
    "id": 7822,
    "artist": "櫻坂46",
    "name": "櫻坂46 「15th Single BACKS LIVE!!」",
    "date": "2026-09-30",
    "dateLabel": "2026年9月29日(火)・30日(水)",
    "venue": "TOYOTA ARENA TOKYO",
    "prefecture": "東京",
    "genre": "new",
    "price": None,
    "links": {
        "rakuten": None, "lawson": U2, "pia": None, "eplus": None,
        "amazon": ("https://www.amazon.co.jp/s?k=%E6%AB%BB%E5%9D%8246"
                   "&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22"),
    },
    "tickets": [
        {"type": "一般発売（東京 9/29・9/30公演）〜9/16 22:00",
         "date": "2026-09-16", "url": U1,
         "soldout": True, "soldoutSince": "2026-09-10"},
        {"type": "一般発売（東京 9/29・9/30公演）9/22 18:00発売",
         "startDate": "2026-09-22", "date": "2026-09-22", "url": U2},
    ],
    "verified": True, "verifiedAt": "2026-09-10",
}

src = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
if any(e['id'] == NEW['id'] for e in events):
    print('!! id%d は既にある。中止' % NEW['id'])
    sys.exit(1)
events.append(NEW)
print('EVENTS %d → %d' % (len(events) - 1, len(events)))
out = (src[:m.start()] + m.group(1)
       + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])

mo = re.search(r'(  const NEW_ORDER = )(\[[^\]]*\])(;)', out, re.S)
arr = json.loads(mo.group(2))
arr2 = [NEW['id']] + [i for i in arr if i != NEW['id']]   # 新着のいちばん上へ
print('NEW_ORDER %d → %d / 先頭 %s' % (len(arr), len(arr2), arr2[:5]))
out = out[:mo.start()] + mo.group(1) + json.dumps(arr2) + mo.group(3) + out[mo.end():]

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
io.open('index.html', 'w', encoding='utf-8').write(out)

h = io.open('index.html', encoding='utf-8').read()
ev = json.loads(re.search(r'  const EVENTS = (\[.*?\]);', h, re.S).group(1))
pool = {e['id'] for e in ev if e.get('genre') == 'new'}
no = json.loads(re.search(r'const NEW_ORDER = (\[[^\]]*\])', h, re.S).group(1))
print('新着プール %d / NEW_ORDER %d / 差 %s %s'
      % (len(pool), len(no), sorted(pool - set(no))[:5], sorted(set(no) - pool)[:5]))
print('書き込み完了')
