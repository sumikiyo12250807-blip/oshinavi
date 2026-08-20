# -*- coding: utf-8 -*-
"""id=2642 第108回全国高等学校野球選手権大会。
ヒールが準決勝(8/20)の7枠を入れてくれたが、7枠とも文言が同じで画面上は区別できない
（[[feedback_pia_parser_flattens_slots]] の型）。ぴあの個別eventCdページの<title>から席種名を取り、
枠ごとに席種を書き分けて、飛び先URLも枠ごとに分ける（[[feedback_dedup_badges_keeps_urls]]）。
エントリの公演日も準々決勝8/18 → 準決勝8/20 に更新する。
"""
import json, re, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

# ぴあ実ページの <title> から機械抽出した席種名（tmp で curl して確認済み）
SEATS = [
    ('2620876', ''),              # 席種名なし（親）
    ('2620877', '中央ボックス席'),
    ('2620878', '1・3塁ボックス席'),
    ('2620879', 'ペア席'),
    ('2620880', 'マス席'),
    ('2620881', '3塁テラス席'),
    ('2620882', '車いす席'),
]
URL = 'https://t.pia.jp/pia/event/event.do?eventCd=%s'

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))

hit = 0
for e in EVENTS:
    if e['id'] != 2642:
        continue
    hit = 1
    old = e.get('tickets') or []
    print('before date=%s 枠=%d' % (e.get('date'), len(old)))
    for t in old:
        print('   ', t['type'])
    if len(old) != len(SEATS):
        print('!! 枠数が %d で想定(%d)と違う。中止する' % (len(old), len(SEATS)))
        sys.exit(1)
    new = []
    for (cd, seat), t in zip(SEATS, old):
        label = '準決勝' + ('・' + seat if seat else '')
        new.append({
            'type': '一般発売【%s】（兵庫 8/20公演）8/19 10:00発売' % label,
            'date': t['date'],
            'startDate': t['startDate'],
            'url': URL % cd,
        })
    e['tickets'] = new
    e['date'] = '2026-08-20'
    e['dateLabel'] = '2026年8月20日(木) 兵庫'
    e['verifiedAt'] = '2026-08-19'
    print('after  date=%s 枠=%d' % (e['date'], len(new)))
    for t in new:
        print('   ', t['type'], t['url'][-8:])

if hit:
    shutil.copyfile('index.html', 'index.html.bak_0819_koshien')
    new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
    open('index.html', 'w', encoding='utf-8').write(h[:m.start()] + m.group(1) + new_arr + m.group(3) + h[m.end():])
    print('=== 更新した ===')
else:
    print('=== id=2642 が見つからない ===')
