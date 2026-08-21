# -*- coding: utf-8 -*-
"""バッジ0（画面に買える枠が出ない）エントリのうち、**e+ に生き枠があった3件**を救済する。

きっかけ＝`node tools/check_zero_badge.js` の「公演まで31日より先なのに枠0」34件を
別エージェントに他社まで当たらせた結果（2026-08-21）。ぴあは0枠でもe+が売っていた。
🚨これが [[feedback_delete_nonpia_blindspot]] の型＝ぴあだけ見て消していたら誤削除だった。

出典（tools/eplus_detail.py で機械抽出・すべて実アクセス確認済み）:
  1601 藍井エイル … https://eplus.jp/sf/detail/0808240001
       熊本10/24・福岡10/25 ＝プレオーダー受付中 〜2026/8/24(月)23:59
       北海道11/28        ＝プレオーダー受付中 〜2026/8/23(日)23:59
  4098 高木いくの … https://eplus.jp/sf/detail/3656540001-P0030002P021001
       東京12/6 ＝一般発売 2026/8/22(土)10:00〜12/3(木)18:00（受付前）
  4115 THE MACKSHOW … https://eplus.jp/sf/detail/0122890001-P0030062P021001
       **福岡**11/18 ＝最終プレオーダー受付中 〜2026/8/24(月)23:59
       🚨登録の県が「宮崎」になっていたが、e+もぴあも **LIVE HOUSE CB は福岡県**。県表記を直す。
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

ADD = {
    1601: [
        {'type': 'プレオーダー受付（熊本 10/24公演）〜8/24 23:59', 'date': '2026-08-24',
         'url': 'https://eplus.jp/sf/detail/0808240001-P0030107P021001'},
        {'type': 'プレオーダー受付（福岡 10/25公演）〜8/24 23:59', 'date': '2026-08-24',
         'url': 'https://eplus.jp/sf/detail/0808240001-P0030108P021001'},
        {'type': 'プレオーダー受付（北海道 11/28公演）〜8/23 23:59', 'date': '2026-08-23',
         'url': 'https://eplus.jp/sf/detail/0808240001-P0030109P021001'},
    ],
    4098: [
        {'type': '一般発売（東京 12/6公演）8/22 10:00発売', 'date': '2026-12-03',
         'startDate': '2026-08-22',
         'url': 'https://eplus.jp/sf/detail/3656540001-P0030002P021001'},
    ],
    4115: [
        {'type': '最終プレオーダー受付（福岡 11/18公演）〜8/24 23:59', 'date': '2026-08-24',
         'url': 'https://eplus.jp/sf/detail/0122890001-P0030062P021001'},
    ],
}
EPLUS_LINK = {
    1601: 'https://eplus.jp/sf/detail/0808240001',
    4098: 'https://eplus.jp/sf/detail/3656540001-P0030002P021001',
    4115: 'https://eplus.jp/sf/detail/0122890001-P0030062P021001',
}

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
n = 0
for e in EVENTS:
    add = ADD.get(e['id'])
    if not add:
        continue
    seen = {(t.get('type'), t.get('url')) for t in e['tickets']}
    print('=== id=%d %s 枠%d' % (e['id'], e.get('artist'), len(e['tickets'])))
    for t in add:
        if (t['type'], t['url']) in seen:
            continue
        e['tickets'].append(t)
        print('    + %s | %s' % (t['type'], t['date']))
    e['links'] = dict(e.get('links') or {}, eplus=EPLUS_LINK[e['id']])
    if e['id'] == 4115:
        print('    県 %s → 福岡（LIVE HOUSE CB は福岡市中央区長浜）' % e.get('prefecture'))
        e['prefecture'] = '福岡'
    e['verifiedAt'] = '2026-08-21'
    print('    → 枠%d' % len(e['tickets']))
    n += 1

assert n == 3, n
shutil.copyfile('index.html', 'index.html.bak_0821_eplus')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('\n=== 3件 救済 ===')
