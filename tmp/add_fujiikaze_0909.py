# -*- coding: utf-8 -*-
"""藤井風 ピアノリサイタル（東京ドーム 11/20・11/21）を新着に1件入れる。

裏取り（2026-09-09 に自分で開いて読んだ）:
  ・公式ニュース https://fujiikaze.com/news-article/news260909/
      公演日 2026年11月20日(金)19時開演 / 11月21日(土)18時開演・東京ドーム
      チケット最速受付（抽選）9/9(水)12:00 〜 9/23(水・祝)23:59
  ・公式特設   https://hehn.fujiikaze.com/fpr/
      販売元 e+ / 指定席 ¥9,000 / 申込は誰でも可（国外在住者を除く）・2枚まで
  ・e+特設     https://eplus.jp/fujiikaze-pianorecital/
      11/20 開場17:00 開演19:00 ／ 11/21 開場16:00 開演18:00 ／ 指定席9,000円
  ※ぴあ検索は0件・e+の通常検索も0件（特設ページ形式のため機械では拾えない）
"""
import io, re, json, sys
sys.path.insert(0, 'tools')
from build_pia_entries import amazon_cd
sys.stdout.reconfigure(encoding='utf-8')

EPLUS = 'https://eplus.jp/fujiikaze-pianorecital/'

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))

assert not [e for e in events if '藤井風' in (e.get('artist') or '') + (e.get('name') or '')], \
    '藤井風のエントリが既にある。中止する'

nid = max(e['id'] for e in events) + 1
entry = {
    "id": nid,
    "artist": "藤井風",
    "name": "藤井風 ピアノリサイタル",
    "date": "2026-11-21",
    "dateLabel": "2026年11月20日(金)〜2026年11月21日(土) 東京 東京ドーム",
    "venue": "東京ドーム",
    "prefecture": "東京",
    "genre": "new",
    "_genre": "jpop",
    "_srcgenre": "eplus",
    "price": "指定席 9,000円",
    "links": {
        "rakuten": None,
        "lawson": None,
        "pia": None,
        "eplus": EPLUS,
        "amazon": amazon_cd("藤井風"),
    },
    "tickets": [
        {
            "type": "チケット最速受付（抽選）（東京 11/20〜11/21公演）〜9/23 23:59",
            "date": "2026-09-23",
            "url": EPLUS,
        }
    ],
    "verified": True,
    "verifiedAt": "2026-09-09",
}
events.append(entry)
print(json.dumps(entry, ensure_ascii=False, indent=2))

# 新着タブの並びは投入順で固定＝NEW_ORDER の末尾に足す
mo = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])', h)
order = json.loads(mo.group(2))
assert nid not in order
order.append(nid)
print('\nNEW_ORDER %d件 → %d件（末尾に %d を追加）' % (len(order) - 1, len(order), nid))

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)

new_events = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n')
h2 = h[:m.start(2)] + new_events + h[m.end(2):]
mo2 = re.search(r'(const NEW_ORDER = )(\[[^\]]*\])', h2)
h2 = h2[:mo2.start(2)] + json.dumps(order) + h2[mo2.end(2):]
io.open('index.html', 'w', encoding='utf-8', newline='').write(h2)
print('書き込み完了 id=%d' % nid)
