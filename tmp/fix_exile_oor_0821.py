# -*- coding: utf-8 -*-
"""② 3518 EXILE を「ドーム公演」と「TOWER RECORDS CAFEのコラボ」に分ける（ユーザー指示 2026-08-21）。
   ③ 4334 ONE OK ROCK の宮城公演を「予定枚数終了」で載せる（同）。

②混ぜていた理由は無く、別種の興行だった＝
  ・EXILE 25th ANNIVERSARY BEST LIVE（ベルーナドーム 11/14・11/15のドーム公演）
  ・EXILE × TOWER RECORDS CAFE 中目黒店（カフェのコラボ予約・8/19〜8/21開催分）
  先例＝3570「BALLISTIK BOYZ from EXILE TRIBE × TOWER RECORDS CAFE」は独立エントリになっている。

③ONE OK ROCK 宮城 8/25・8/26（セキスイハイムスーパーアリーナ）は
  **GIP が「SOLD OUT」と明記**（https://www.gip-web.co.jp/t/ONEOKROCK）＝**予定枚数終了**。
  ぴあの実ページでも当該2枠は受付終了。売り切れは消さず出し続ける（[[feedback_soldout_keep_visible]]）。
  🚨枠ごとに付ける（エントリ一括マーク禁止＝[[feedback_saleended_vs_soldout]]）。
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}
newid = max(e['id'] for e in EVENTS) + 1

# ② 3518 を分ける
e = by[3518]
cafe = [t for t in e['tickets'] if '中目黒店' in (t.get('type') or '')]
dome = [t for t in e['tickets'] if '中目黒店' not in (t.get('type') or '')]
print('② 3518 EXILE 枠%d → ドーム%d ／ カフェ%d' % (len(e['tickets']), len(dome), len(cafe)))
e['tickets'] = dome
e['name'] = e['artist'] = 'EXILE'
e['venue'] = 'ベルーナドーム'
e['prefecture'] = '埼玉'
e['dateLabel'] = '2026年11月14日(土)〜2026年11月15日(日) 埼玉 ベルーナドーム'
e['verifiedAt'] = '2026-08-21'
for t in dome:
    print('   [ドーム]', t['type'])

cafe_entry = {
    'id': newid,
    'artist': 'EXILE',
    'name': 'EXILE × TOWER RECORDS CAFE',
    'date': '2026-08-21',
    'dateLabel': '2026年8月19日(水)〜2026年8月21日(金) 東京 TOWER RECORDS CAFE 中目黒店',
    'venue': 'TOWER RECORDS CAFE 中目黒店',
    'prefecture': '東京',
    'genre': e.get('genre'),
    'price': None,
    'links': {'rakuten': None, 'lawson': None,
              'pia': 'https://t.pia.jp/pia/event/event.do?eventCd=2617158', 'eplus': None},
    'tickets': cafe,
    'verified': True,
    'verifiedAt': '2026-08-21',
}
for t in cafe:
    print('   [カフェ]', t['type'])
EVENTS.append(cafe_entry)
print('   → 新エントリ id=%d %s' % (newid, cafe_entry['name']))

# ③ ONE OK ROCK 宮城を予定枚数終了で載せる
o = by[4334]
add = [
    {'type': '一般発売（宮城 8/25公演）〜8/24 23:59', 'date': '2026-08-24',
     'url': 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669955', 'soldout': True},
    {'type': '一般発売（宮城 8/26公演）〜8/25 23:59', 'date': '2026-08-25',
     'url': 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669955', 'soldout': True},
]
seen = {(t.get('type'), t.get('url')) for t in o['tickets']}
print('\n③ 4334 ONE OK ROCK 枠%d' % len(o['tickets']))
for t in add:
    if (t['type'], t['url']) in seen:
        continue
    o['tickets'].append(t)
    print('   + %s ← 予定枚数終了（GIPが SOLD OUT と明記）' % t['type'])
o['venue'] = '全国ツアー（ZOZOマリンスタジアム／宮城・セキスイハイムスーパーアリーナ（グランディ・21））'
o['prefecture'] = '千葉・宮城'
o['verifiedAt'] = '2026-08-21'
print('   → 枠%d' % len(o['tickets']))

shutil.copyfile('index.html', 'index.html.bak_0821_split')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('\n=== %d件 → %d件 ===' % (len(EVENTS) - 1, len(EVENTS)))
