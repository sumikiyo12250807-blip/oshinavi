# -*- coding: utf-8 -*-
"""はなもも マリンバ&打楽器コンサート（岐阜 9/26）を新着に1件入れる。

出どころ＝e+ 検索で「藤井風」に引っかかった（曲目に「きらり/藤井風」が入っているため）。
機械で読んだ実データ（python tools/eplus_detail.py）:
  2026/9/26(土) 揖斐川町地域交流センターはなもも ホール（岐阜県）
  [LIVE] 受付中 | 先着 一般発売 | 受付期間 2026/7/25(土)10:00～2026/9/25(金)18:00
実ページで確認した中身: 開演14:00(開場13:00) / 出演 L' eau Claire
"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

URL = 'https://eplus.jp/sf/detail/4566210001-P0030001P021001'

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))

assert not [e for e in events if 'マリンバ&打楽器' in (e.get('name') or '')], '既にある。中止'
assert not [e for e in events if URL in json.dumps(e, ensure_ascii=False)], '同じURLが既にある。中止'

nid = max(e['id'] for e in events) + 1
entry = {
    "id": nid,
    "artist": "L’ eau Claire",
    "name": "はなもも マリンバ&打楽器コンサート",
    "date": "2026-09-26",
    "dateLabel": "2026年9月26日(土) 岐阜 揖斐川町地域交流センターはなもも ホール",
    "venue": "揖斐川町地域交流センターはなもも ホール",
    "prefecture": "岐阜",
    "genre": "new",
    "_genre": "classic",
    "_srcgenre": "eplus",
    "price": None,
    "links": {"rakuten": None, "lawson": None, "pia": None, "eplus": URL, "amazon": None},
    "tickets": [
        {
            "type": "先着 一般発売（岐阜 9/26公演）〜9/25 18:00",
            "date": "2026-09-25",
            "url": URL,
        }
    ],
    "verified": True,
    "verifiedAt": "2026-09-09",
}
events.append(entry)
print(json.dumps(entry, ensure_ascii=False, indent=2))

mo = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])', h)
order = json.loads(mo.group(2))
assert nid not in order
order.append(nid)
print('\nNEW_ORDER %d件 → %d件' % (len(order) - 1, len(order)))

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
h2 = h[:m.start(2)] + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + h[m.end(2):]
mo2 = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])', h2)
h2 = h2[:mo2.start(2)] + json.dumps(order) + h2[mo2.end(2):]
io.open('index.html', 'w', encoding='utf-8', newline='').write(h2)
print('書き込み完了 id=%d' % nid)
