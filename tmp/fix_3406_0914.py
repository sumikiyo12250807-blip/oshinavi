# -*- coding: utf-8 -*-
"""3406 反田恭平&ザルツブルク・モーツァルテウム管弦楽団 日本ツアー2027＝X主役に出すので取りこぼしを潰す（2026-09-14 夜）。
ぴあの取り直し（tmp/heal_ids.json・5枠）＝川崎3/15 プリセール(9/15)・川崎 一般発売WEB受付(9/22)・福岡3/17 一般発売(9/27)・倉敷3/16・東京3/25。
安全弁が止めた＝登録の京都3/22 が取り直しに無い＝ぴあ「予定枚数終了」（tmp/x0914/shuyaku.md）→ 京都は売り切れの印を付けて残す（消さない）。
会期は事実で書く＝フジテレビ公式の全9公演 3/15 川崎〜3/27 札幌（名古屋・仙台・新潟・札幌はぴあに無い）→ date・dateLabel・県・会場を直す。
使い方: python tmp/fix_3406_0914.py [--apply]
"""
import datetime
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
TODAY = datetime.date.today().isoformat()
src = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 3406)
built = next(o for o in json.load(io.open('tmp/heal_ids.json', encoding='utf-8')) if o['id'] == 3406)
assert built['status'] == 'convert' and len(built['tickets']) == 5, built
kyoto = [t for t in e['tickets'] if '京都' in (t.get('type') or '') and '3/22' in (t.get('type') or '')]
assert len(kyoto) == 1, [t['type'] for t in e['tickets']]
k = dict(kyoto[0])
k['soldout'] = True
k['soldoutSince'] = TODAY
print('残す（売り切れの印）: %s' % k['type'])
old = [t['type'] for t in e['tickets']]
e['tickets'] = [dict(t) for t in built['tickets']] + [k]
print('元の枠: ' + ' ／ '.join(old))
print('新しい枠: ' + ' ／ '.join(t['type'] for t in e['tickets']))
new = {
    'date': '2027-03-27',
    'dateLabel': '2027年3月15日(月)〜2027年3月27日(土) 全国',
    'prefecture': '全国',
    'venue': '全国ツアー（ミューザ川崎シンフォニーホール／倉敷市民会館／アクロス福岡 福岡シンフォニーホール／愛知県芸術劇場 コンサートホール／'
             '仙台銀行ホールイズミティ21 大ホール／りゅーとぴあ 新潟市民芸術文化会館 コンサートホール／京都コンサートホール 大ホール／'
             '東京オペラシティ コンサートホール／札幌コンサートホール Kitara 大ホール）',
}
for key, v in new.items():
    print('%-10s %s\n        → %s' % (key, e.get(key), v))
    e[key] = v
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
out = src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl) + m.group(3) + src[m.end():]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
