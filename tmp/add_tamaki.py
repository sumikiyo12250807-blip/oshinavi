# -*- coding: utf-8 -*-
import re, json

LTIKE = "https://l-tike.com/order/?gLcode=42464&gPfKey=20260427000002194858&gEntryMthd=03&gScheduleNo=2&gCarrierCd=01&gPfName=%E7%8E%89%E7%BD%AE%E6%B5%A9%E4%BA%8C&gBaseVenueCd=45507"
EPLUS = "https://eplus.jp/sf/detail/0011860001"

entry = {
    "id": 3011,
    "artist": "玉置浩二",
    "name": "玉置浩二 with 故郷楽団 Concert Tour 2026 ファンファーレ!!",
    "date": "2026-10-21",
    "dateLabel": "2026年9月9日(水)〜2026年10月21日(水) 全国ツアー アクトシティ浜松 大ホール／福岡サンパレス／ベネックス長崎ブリックホール 大ホール／熊本城ホール メインホール",
    "venue": "全国ツアー（アクトシティ浜松 大ホール／福岡サンパレス／ベネックス長崎ブリックホール 大ホール／熊本城ホール メインホール）",
    "prefecture": "全国",
    "genre": "jpop",
    "price": "13,000円",
    "links": {
        "rakuten": None,
        "lawson": LTIKE,
        "pia": None,
        "eplus": EPLUS,
        "amazon": "https://www.amazon.co.jp/s?k=%E7%8E%89%E7%BD%AE%E6%B5%A9%E4%BA%8C%20CD&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22"
    },
    "tickets": [
        {"type": "抽選プレリク先行（静岡 9/9公演）〜7/27 23:59", "date": "2026-07-27", "startDate": "2026-07-21", "url": LTIKE},
        {"type": "抽選☆プレオーダー（福岡 10/1公演）〜7/26 23:59", "date": "2026-07-26", "startDate": "2026-07-21", "url": EPLUS},
        {"type": "抽選☆プレオーダー（福岡 10/2公演）〜7/26 23:59", "date": "2026-07-26", "startDate": "2026-07-21", "url": EPLUS},
        {"type": "抽選☆プレオーダー（長崎 10/4公演）〜7/26 23:59", "date": "2026-07-26", "startDate": "2026-07-21", "url": EPLUS},
        {"type": "抽選☆プレオーダー（熊本 10/21公演）〜7/26 23:59", "date": "2026-07-26", "startDate": "2026-07-21", "url": EPLUS},
    ],
    "verified": True,
    "verifiedAt": "2026-07-21"
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
assert not any(e['id'] == 3011 for e in EVENTS), "id 3011 already exists"
EVENTS.append(entry)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print("追加完了 全件数:", len(EVENTS))
