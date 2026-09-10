# -*- coding: utf-8 -*-
"""女王蜂(id4802)に Zepp Fukuoka 10/25 の枠を足す。

裏取り＝
 ①公式(ソニーミュージック)＝『女王蜂 全国ツアー2026「星」』は5会場
   10/11 Zepp Sapporo ／10/18 Zepp Osaka Bayside ／10/23 Zepp Nagoya ／
   **10/25 Zepp Fukuoka** ／10/30 Zepp Haneda(TOKYO)
   https://www.sonymusic.co.jp/artist/ziyoou-vachi/info/584961
 ②ぴあには福岡が無い（"女王蜂"の総ざらいで4件だけ）
 ③e+に5会場ぜんぶある。福岡は「抽選 最終先行」が受付中（2026/9/7 12:00〜9/13 23:59）
   https://eplus.jp/sf/detail/0521750001-P0030299P021001

🚨links には触らない＝画面の購入ボタンの飛び先を変えない。枠のurlだけ持たせる
   （[[feedback_tour_per_ticket_url]]／楽天リンクで飛び先を壊した型を繰り返さない）。
🚨CRLFを壊さない・書き戻しの形は refresh_deadlines_0909.py と揃える。

使い方: python tmp/add_qb_fukuoka_0910.py [--apply]
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv

NEW = {
    'type': '最終先行（福岡 10/25公演）〜9/13 23:59',
    'date': '2026-09-13',
    'url': 'https://eplus.jp/sf/detail/0521750001-P0030299P021001',
}
VENUE = ('全国ツアー（Zepp Sapporo／Zepp Osaka Bayside／Zepp Nagoya／'
         'Zepp Fukuoka／Zepp Haneda（TOKYO））')

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))

for e in events:
    if e['id'] != 4802:
        continue
    tks = e.setdefault('tickets', [])
    if any('福岡' in (t.get('type') or '') for t in tks):
        print('すでに福岡の枠がある＝何もしない')
        sys.exit(0)
    print('## id=4802 %s' % e.get('artist'))
    print('   会場  %s' % e.get('venue'))
    print('       → %s' % VENUE)
    print('   枠 %d → %d' % (len(tks), len(tks) + 1))
    print('   ＋%s' % NEW['type'])
    e['venue'] = VENUE
    tks.append(NEW)
    break
else:
    print('id=4802 が見つからない')
    sys.exit(1)

if APPLY:
    body = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n')
    io.open('index.html', 'w', encoding='utf-8', newline='').write(
        h[:m.start(2)] + body + h[m.end(2):])
    print('書き込み完了')
else:
    print('(--apply で書き込み)')
