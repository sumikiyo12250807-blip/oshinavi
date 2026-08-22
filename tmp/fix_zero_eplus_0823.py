# -*- coding: utf-8 -*-
"""バッジ0だった e+ 由来の2件に、実ページで確認した買える枠を入れる（2026-08-23朝）。

  id43   シナモロール … 福岡公演の一般発売が受付中（登録は「8/22 10:00発売」のまま＝締切が入っていない隠れ枠）
  id3085 浦島坂田船   … 東京10/10・10/11／兵庫10/24・10/25 の☆X先行が受付中（兵庫は未登録）

根拠＝tools/eplus_detail.py の実ページ出力（tmp/eplus43_0823.txt / tmp/eplus3085_0823.txt）。
公演時間は生HTMLの「開演」から取った（同日2公演があるので必須 [[feedback_same_day_show_time_badge]]）。
枠ごとに url を刻む（飛び先が違えば別の売り場）。
"""
import re, io, json, sys
sys.stdout.reconfigure(encoding='utf-8')

APPLY = '--apply' in sys.argv

h = io.open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
by = {e['id']: e for e in EVENTS}

# ── id43 シナモロール（福岡 久留米シティプラザ ザ・グランドホール）
e = by[43]
OLD = '一般発売（福岡 10/10〜10/11公演）8/22 10:00発売'
before = len(e['tickets'])
e['tickets'] = [t for t in e['tickets'] if t.get('type') != OLD]
e['tickets'] += [
    {'type': '一般発売（福岡 10/10 17:00公演）〜10/9 20:00', 'date': '2026-10-09',
     'url': 'https://eplus.jp/sf/detail/4518110001-P0030003P021003'},
    {'type': '一般発売（福岡 10/11 11:30公演）〜10/10 20:00', 'date': '2026-10-10',
     'url': 'https://eplus.jp/sf/detail/4518110001-P0030003P021001'},
    {'type': '一般発売（福岡 10/11 15:30公演）〜10/10 20:00', 'date': '2026-10-10',
     'url': 'https://eplus.jp/sf/detail/4518110001-P0030003P021002'},
]
e['links']['eplus'] = 'https://eplus.jp/sf/detail/4518110001-P0030003P021003'
e['verifiedAt'] = '2026-08-23'
print('id43   枠 %d → %d' % (before, len(e['tickets'])))

# ── id3085 浦島坂田船（有明アリーナ／神戸ワールド記念ホール）
e = by[3085]
before = len(e['tickets'])
have = {t.get('type') for t in e['tickets']}
for ty, d, u in [
    ('☆X先行（東京都 10/10公演）〜8/24 23:59', '2026-08-24', 'https://eplus.jp/sf/detail/1067170001-P0030271P021002'),
    ('☆X先行（東京都 10/11公演）〜8/24 23:59', '2026-08-24', 'https://eplus.jp/sf/detail/1067170001-P0030271P021001'),
    ('☆X先行（兵庫県 10/24公演）〜8/24 23:59', '2026-08-24', 'https://eplus.jp/sf/detail/1067170001-P0030272P021002'),
    ('☆X先行（兵庫県 10/25公演）〜8/24 23:59', '2026-08-24', 'https://eplus.jp/sf/detail/1067170001-P0030272P021001'),
]:
    if ty not in have:
        e['tickets'].append({'type': ty, 'date': d, 'url': u})
e['date'] = '2026-10-25'
e['dateLabel'] = '2026年8月7日(金)〜2026年10月25日(日) 全国ツアー'
e['venue'] = '全国ツアー（LaLa arena TOKYO-BAY／大阪城ホール／有明アリーナ／神戸ワールド記念ホール）'
e['verifiedAt'] = '2026-08-23'
print('id3085 枠 %d → %d / 千秋楽 2026-10-10 → 2026-10-25' % (before, len(e['tickets'])))

for i in (43, 3085):
    types = [t.get('type') for t in by[i]['tickets']]
    dup = [x for x in set(types) if types.count(x) > 1]
    if dup:
        print('🚨 SAME-BADGE id%d: %s' % (i, dup))
        sys.exit(2)

if APPLY:
    io.open('index.html.bak_0823_eplusfix', 'w', encoding='utf-8').write(h)
    io.open('index.html', 'w', encoding='utf-8').write(
        h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
    print('適用した')
else:
    print('（見ただけ。適用は --apply）')
