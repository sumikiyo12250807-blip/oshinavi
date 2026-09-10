# -*- coding: utf-8 -*-
"""ローチケ独占3件を新着プールへ投入する（2026-09-10）。

素材＝実ブラウザでローチケのチケット詳細ページを開いて画面から読んだもの
（[[reference_ltike_machine_unreachable]]）。URLは data-* から組み立てて **実際に開いて200を確認済み**。
🚨gEntryMthd は固定の02ではなく data-rcptypename の値（別府葉子・野田＝01／REVERSE EDGE＝02）。

ユーザー指示（2026-09-10）＝「しんちゃくのうえのほうにのせておいて」
→ 今日足した分（7812〜）ごと NEW_ORDER の**先頭**へ移す。
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

RE1 = ('https://l-tike.com/order/?gLcode=72049&gPfKey=20260831000002286720&gEntryMthd=02'
       '&gScheduleNo=1&gCarrierCd=08&gPfName=%EF%BC%B2%EF%BC%A5%EF%BC%B6%EF%BC%A5%EF%BC%B2'
       '%EF%BC%B3%EF%BC%A5%E3%80%80%EF%BC%A5%EF%BC%A4%EF%BC%A7%EF%BC%A5%E3%80%80%EF%BC%92'
       '&gBaseVenueCd=34027')
RE2 = RE1.replace('gScheduleNo=1', 'gScheduleNo=2')
BEPPU = ('https://l-tike.com/order/?gLcode=55384&gPfKey=20260908000002291683&gEntryMthd=01'
         '&gScheduleNo=1&gCarrierCd=08&gPfName=%E5%88%A5%E5%BA%9C%E8%91%89%E5%AD%90'
         '&gBaseVenueCd=53158')
NODA = ('https://l-tike.com/order/?gLcode=82465&gPfKey=20260907000002290717&gEntryMthd=01'
        '&gScheduleNo=1&gCarrierCd=08&gPfName=%E9%87%8E%E7%94%B0%E3%81%8B%E3%81%A4%E3%81%B2'
        '%E3%81%93&gBaseVenueCd=81776')
AMZ = ('https://www.amazon.co.jp/s?k=%s&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22')

NEW = [
    {
        "id": 7819,
        "artist": "環ROY／ぷにぷに電機／Bucket Drummer MASA",
        "name": "REVERSE EDGE 2 - SUPERNOVA KAWASAKI 3rd Anniversary Future Energy Live",
        "date": "2026-11-02",
        "dateLabel": "2026年11月2日(月)",
        "venue": "SUPERNOVA KAWASAKI",
        "prefecture": "神奈川",
        "genre": "new",
        "price": None,
        "links": {"rakuten": None, "lawson": RE2, "pia": None, "eplus": None},
        "tickets": [
            {"type": "プレリク先行（神奈川 11/2公演）〜9/13 23:59",
             "date": "2026-09-13", "url": RE1},
            {"type": "一般発売（神奈川 11/2公演）9/19 10:00発売",
             "startDate": "2026-09-19", "date": "2026-09-19", "url": RE2},
        ],
        "verified": True, "verifiedAt": "2026-09-10",
    },
    {
        "id": 7820,
        "artist": "別府葉子",
        "name": "別府葉子シャンソンコンサート in OSAKA ＜LOVE STORY＞",
        "date": "2026-12-19",
        "dateLabel": "2026年12月19日(土)",
        "venue": "国際楽器社ホール",
        "prefecture": "大阪",
        "genre": "new",
        "price": None,
        "links": {"rakuten": None, "lawson": BEPPU, "pia": None, "eplus": None,
                  "amazon": AMZ % '%E5%88%A5%E5%BA%9C%E8%91%89%E5%AD%90'},
        "tickets": [
            {"type": "一般発売（大阪 12/19公演）9/20 10:00発売",
             "startDate": "2026-09-20", "date": "2026-09-20", "url": BEPPU},
        ],
        "verified": True, "verifiedAt": "2026-09-10",
    },
    {
        "id": 7821,
        "artist": "野田かつひこ",
        "name": "Life History2026 ふるさとの唄 野田かつひこコンサート",
        "date": "2026-12-15",
        "dateLabel": "2026年12月15日(火)",
        "venue": "石橋文化ホール",
        "prefecture": "福岡",
        "genre": "new",
        "price": None,
        "links": {"rakuten": None, "lawson": NODA, "pia": None, "eplus": None,
                  "amazon": AMZ % '%E9%87%8E%E7%94%B0%E3%81%8B%E3%81%A4%E3%81%B2%E3%81%93'},
        "tickets": [
            {"type": "一般発売（福岡 12/15公演）9/14 10:00発売",
             "startDate": "2026-09-14", "date": "2026-09-14", "url": NODA},
        ],
        "verified": True, "verifiedAt": "2026-09-10",
    },
]

# 今日ローチケ由来で足した分＝新着の先頭に持ち上げる
TOP = [7819, 7820, 7821, 7812, 7813, 7814, 7815, 7816, 7818]

src = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
have = {e['id'] for e in events}
for e in NEW:
    if e['id'] in have:
        print('!! id%d は既にある。中止' % e['id'])
        sys.exit(1)
events.extend(NEW)
print('EVENTS %d → %d' % (len(events) - len(NEW), len(events)))
out = (src[:m.start()] + m.group(1)
       + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])

mo = re.search(r'(  const NEW_ORDER = )(\[[^\]]*\])(;)', out, re.S)
arr = json.loads(mo.group(2))
rest = [i for i in arr if i not in TOP]
arr2 = TOP + rest
print('NEW_ORDER %d → %d（先頭9件を今日の分に）' % (len(arr), len(arr2)))
print('  先頭:', arr2[:12])
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
