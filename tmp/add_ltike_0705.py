# -*- coding: utf-8 -*-
"""7/5 ローチケ本日発売の手動追加2件(木梨憲武展札幌/ゴジラTHEアート展神戸)。
エージェントがリーダー経由でURL・日付・受付中を裏取り済み。genre:"new"プール。
※アートジャンル無し→_genre空・要ジャンル判断(⚠️相談)。"""
import re, json, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
DRY = '--apply' not in sys.argv

NEW = [
  {
    "id": 2034,
    "artist": "木梨憲武展 -TOUCH SERENDIPITY-",
    "name": "木梨憲武展 -TOUCH SERENDIPITY- 意味ある偶然（札幌）",
    "date": "2026-08-22",
    "dateLabel": "2026年7月5日(日)〜8月22日(土)",
    "venue": "サッポロファクトリー3条館3階",
    "prefecture": "北海道",
    "genre": "new",
    "_genre": "",
    "_extraGenres": [],
    "_piaSub": "アート(要ジャンル判断)",
    "price": None,
    "links": {"rakuten": None, "lawson": "https://l-tike.com/event/mevent/?mid=747350",
              "pia": None, "eplus": None, "amazon": None},
    "tickets": [
      {"type": "一般発売 先着（北海道 7/5〜8/22会期）本日発売", "date": "2026-08-22", "saleUntilSoldOut": True}
    ],
    "verified": True,
    "verifiedAt": "2026-07-05"
  },
  {
    "id": 2035,
    "artist": "ゴジラ・THE・アート展",
    "name": "ゴジラ生誕70周年記念 ゴジラ・THE・アート展",
    "date": "2026-09-06",
    "dateLabel": "2026年7月5日(日)〜9月6日(日)",
    "venue": "神戸ゆかりの美術館",
    "prefecture": "兵庫県",
    "genre": "new",
    "_genre": "",
    "_extraGenres": [],
    "_piaSub": "アート(要ジャンル判断)",
    "price": None,
    "links": {"rakuten": None, "lawson": "https://l-tike.com/event/mevent/?mid=746343",
              "pia": None, "eplus": None, "amazon": None},
    "tickets": [
      {"type": "当日券 一般発売 先着（兵庫 7/5〜9/6会期）本日発売", "date": "2026-09-06", "saleUntilSoldOut": True}
    ],
    "verified": True,
    "verifiedAt": "2026-07-05"
  }
]

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
have = {e.get('id') for e in EVENTS}
add = [e for e in NEW if e['id'] not in have]
print(f"追加 {len(add)}件 / 既存衝突 {[e['id'] for e in NEW if e['id'] in have]}")

EVENTS2 = EVENTS + add
new_arr = json.dumps(EVENTS2, ensure_ascii=False, indent=2)
# NEW_ORDERに追記
mo = re.search(r'const NEW_ORDER = (\[[0-9,\s]*\]);', h)
cur = json.loads(mo.group(1))
for e in add:
    if e['id'] not in cur:
        cur.append(e['id'])
no = '[' + ', '.join(str(i) for i in cur) + ']'
h2 = h[:mo.start()] + 'const NEW_ORDER = ' + no + ';' + h[mo.end():]
h3 = h2[:m.start()] + m.group(1) + new_arr + m.group(3) + h2[m.end():]

if DRY:
    print(f"(DRY) NEW_ORDER {len(cur)}件になる")
else:
    open('index.html.bak_0705_ltike', 'w', encoding='utf-8').write(h)
    open('index.html', 'w', encoding='utf-8').write(h3)
    print(f"written (backup: index.html.bak_0705_ltike) NEW_ORDER {len(cur)}件")
