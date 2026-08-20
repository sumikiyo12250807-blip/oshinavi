# -*- coding: utf-8 -*-
"""真田ナオキ：id775を「コンサート2026」ツアー統合形に置換し、
浅草ディスコLIVE・ランチ&ディナーショーを新エントリで追加する。"""
import re, json, sys, datetime
sys.stdout.reconfigure(encoding='utf-8')

AMZ = "https://www.amazon.co.jp/s?k=%E7%9C%9F%E7%94%B0%E3%83%8A%E3%82%AA%E3%82%AD%20CD&i=specialty-aps&srs=26200021051&tag=oshinavi0a-22"
D = 'https://eplus.jp/sf/detail/'

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
byid = {e['id']: e for e in EVENTS}

# ---- A: id775 = 真田ナオキ コンサート2026（単独コンサートツアー統合） ----
a = byid[775]
a['name'] = '真田ナオキ コンサート2026'
a['date'] = '2026-11-22'
a['dateLabel'] = ('2026年8月1日(土)京都／9月14日(月)愛知／9月22日(火)兵庫／'
                  '9月24日(木)福岡／9月25日(金)熊本／11月22日(日)大阪')
a['venue'] = ('京都劇場／Niterra日本特殊陶業市民会館／アクリエひめじ／'
              '福岡市民ホール／くまもと森都心プラザ／サンケイホールブリーゼ')
a['prefecture'] = '京都・愛知・兵庫・福岡・熊本・大阪'
a['genre'] = 'enka'
a['price'] = '全席指定 7,700円'
a['tickets'] = [
    {"type": "一般発売（京都 8/1公演）〜7/29 18:00", "date": "2026-07-29",
     "url": D + "3489620001-P0030046P021001"},
    {"type": "一般発売（愛知 9/14公演）〜9/11 18:00", "date": "2026-09-11",
     "url": D + "3489620001-P0030050P021001"},
    {"type": "一般発売（兵庫 9/22公演）〜9/21 18:00", "date": "2026-09-21",
     "url": D + "4534110001-P0030001P021001"},
    {"type": "一般発売（福岡・熊本 9/24〜9/25公演）〜9/23 23:59", "date": "2026-09-23",
     "url": "https://t.pia.jp/pia/event/event.do?eventCd=2612529"},
    {"type": "一般発売（大阪 11/22公演）7/30 10:00発売", "date": "2026-11-14",
     "startDate": "2026-07-30", "url": D + "3489620001-P0030055P021001"},
]
a['links']['eplus'] = D + '3489620001'
a['verified'] = True
a['verifiedAt'] = '2026-07-24'

# ---- B: 浅草ディスコLIVE 2026（真田単独ライブ・別企画） ----
B = {
    "id": 3166, "artist": "真田ナオキ", "name": "真田ナオキLIVE2026 浅草ディスコ",
    "date": "2026-10-24",
    "dateLabel": "2026年10月23日(金)〜10月24日(土) 東京 浅草公会堂",
    "venue": "浅草公会堂", "prefecture": "東京", "genre": "enka", "price": None,
    "links": {"rakuten": None, "lawson": None, "pia": None,
              "eplus": D + "3489620001", "amazon": AMZ},
    "tickets": [
        {"type": "一般発売（東京 10/23公演）7/31 12:00発売", "date": "2026-10-20",
         "startDate": "2026-07-31", "url": D + "3489620001-P0030053P021001"},
        {"type": "一般発売（東京 10/24公演）7/31 12:00発売", "date": "2026-10-21",
         "startDate": "2026-07-31", "url": D + "3489620001-P0030053P021002"},
    ],
    "verified": True, "verifiedAt": "2026-07-24",
}

# ---- C: ランチ&ディナーショー（川越・同日昼夜） ----
C = {
    "id": 3167, "artist": "真田ナオキ", "name": "真田ナオキ ランチ&ディナーショー",
    "date": "2026-08-22",
    "dateLabel": "2026年8月22日(土) 埼玉 川越プリンスホテル",
    "venue": "川越プリンスホテル", "prefecture": "埼玉", "genre": "enka", "price": None,
    "links": {"rakuten": None, "lawson": None, "pia": None,
              "eplus": D + "4549640001", "amazon": AMZ},
    "tickets": [
        {"type": "一般発売（埼玉 8/22 12:00公演）〜8/15 18:00", "date": "2026-08-15",
         "url": D + "4549640001-P0030001P021001"},
        {"type": "一般発売（埼玉 8/22 17:00公演）〜8/15 18:00", "date": "2026-08-15",
         "url": D + "4549640001-P0030001P021002"},
    ],
    "verified": True, "verifiedAt": "2026-07-24",
}

assert 3166 not in byid and 3167 not in byid, 'id重複'
EVENTS.append(B); EVENTS.append(C)

bak = 'index.html.bak_0724_sanada'
open(bak, 'w', encoding='utf-8').write(h)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
print(f'A(id775)統合5枠 / B(3166浅草)2枠 / C(3167川越)2枠 追加 / 総{len(EVENTS)}件 (backup {bak})')
