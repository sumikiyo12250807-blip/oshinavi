# -*- coding: utf-8 -*-
"""新日本プロレス 赤磐 11/1（ローチケだけ）を新着プールへ入れる（2026-09-15夜）。
X投稿の主役②新日本プロレスの取りこぼしチェック（ユーザー「xに取り上げる時は取りこぼしチェックは必須よ」）で、
公式の日程（njpw.co.jp/tournament/662780）にあってぴあ・e+ に無く、ローチケにだけ「プレリクエスト先着先行＝発売中」があった。
素材＝実ブラウザでローチケの購入ページ2枚を開いて画面から読んだもの（URLは開いて中身が出るのを確認済み）：
  プレリク先行＝受付 2026/9/13(日) 12:00 〜 9/19(土) 23:59（Web のみ・Loppi店頭なし）
  一般販売　　＝受付 2026/9/20(日) 10:00 〜 11/1(日) 18:00（発売前）
  2026/11/1(日) 開場16:00 開始17:00 山陽ふれあい公園総合体育館（岡山県）
ぴあ以外なので振り分けはユーザーの確認のあと（新着に置くだけ）。価格はローチケ1か所なので入れない。改行は CRLF を保つ。
使い方: python tmp/x0916/add_akaiwa_ltike.py [--apply]
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
BASE = ('https://l-tike.com/order/?gLcode=61733&gPfKey=20260826000002282756&gEntryMthd=%s'
        '&gScheduleNo=1&gCarrierCd=01&gPfName=%%E6%%96%%B0%%E6%%97%%A5%%E6%%9C%%AC%%E3%%83%%97%%E3%%83%%AD'
        '%%E3%%83%%AC%%E3%%82%%B9%%E3%%80%%80%%E8%%B5%%A4%%E7%%A3%%90&gBaseVenueCd=69584')
PRE = BASE % '02'
GEN = BASE % '01'
NEW_ID = 10762
ENTRY = {
    "id": NEW_ID,
    "artist": "新日本プロレス",
    "name": "新日本プロレス 赤磐",
    "date": "2026-11-01",
    "dateLabel": "2026年11月1日(日) 岡山 山陽ふれあい公園総合体育館",
    "venue": "山陽ふれあい公園総合体育館",
    "prefecture": "岡山",
    "genre": "new",
    "_genre": "sports",
    "price": None,
    "links": {"rakuten": None, "lawson": GEN, "pia": None, "eplus": None},
    "tickets": [
        {"type": "プレリク先行（岡山 11/1公演）〜9/19 23:59", "date": "2026-09-19", "url": PRE},
        {"type": "一般発売（岡山 11/1公演）9/20 10:00発売", "startDate": "2026-09-20", "date": "2026-09-20", "url": GEN},
    ],
    "verified": True,
    "verifiedAt": "2026-09-15",
}

src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
assert NEW_ID not in {e['id'] for e in events}, 'id%s はもう使われている' % NEW_ID
events.append(ENTRY)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
mo = re.search(r'const NEW_ORDER = \[([^\]]*)\];', out)
order = [int(x) for x in mo.group(1).split(',') if x.strip()]
order.append(NEW_ID)
out = out[:mo.start()] + 'const NEW_ORDER = [%s];' % ', '.join(str(x) for x in order) + out[mo.end():]
print('id%s %s ｜%s ｜枠%d ／ NEW_ORDER %d件（末尾に足す）' % (NEW_ID, ENTRY['name'], ENTRY['dateLabel'], len(ENTRY['tickets']), len(order)))
if '--apply' not in sys.argv:
    print('（--apply で書き込み）')
    sys.exit(0)
open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
