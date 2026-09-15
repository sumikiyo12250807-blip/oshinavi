# -*- coding: utf-8 -*-
"""9/15夜の総ざらいで足した分の後始末（別エージェントの独立の読み直しの指摘・2026-09-15夜）。
1) 10741 ヘルシンキ・フィル with 角野隼斗＝会期（〜10/18）と会場欄には入っているのに枠が無い3公演を、
   ぴあの「予定枚数終了」どおり売り切れの印付きで足す（売り切れは消さずに出す＝feedback_soldout_keep_visible／
   9/15朝の Chevon と同じ扱い「売り切れの印付きで足しておいて」）。
   東京 10/13 サントリーホール（eventCd=2610028）／長野 10/17 上田（2618908）／神奈川 10/18 横浜みなとみらい（2606307）
   締切はぴあが出していない＝枠の date は公演の前日にしない。売り切れ枠は公演日を過ぎたら画面から消える（renderCard の安全弁）ので date＝公演日。
2) 足し込んだ4件の会場欄（venue）に、足した会場名が入っていない → 足す（dateLabel・prefecture は merge 時に作り直し済み）。
使い方: python tmp/x0916/fix_eve_0915.py [--apply]
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
APPLY = '--apply' in sys.argv
TODAY = '2026-09-15'

SOLD = [
    ('一般発売（東京 10/13公演）', '2026-10-13', 'https://t.pia.jp/pia/event/event.do?eventCd=2610028'),
    ('一般発売（長野 10/17公演）', '2026-10-17', 'https://t.pia.jp/pia/event/event.do?eventCd=2618908'),
    ('一般発売（神奈川 10/18公演）', '2026-10-18', 'https://t.pia.jp/pia/event/event.do?eventCd=2606307'),
]
VENUE_ADD = {
    8145: ['仙台PIT', '広島クラブクアトロ', '高松MONSTER', 'NIIGATA LOTS'],
    8404: ['ベネックス長崎ブリックホール 国際会議場', 'NCBホール'],
    2468: ['サンエールかごしま ホール'],
    2243: ['兵庫県立芸術文化センター KOBELCO大ホール'],
}

src = open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
byid = {e['id']: e for e in events}

e = byid[10741]
have = {t['type'].split('〜')[0] for t in e['tickets']}
for typ, d, u in SOLD:
    if typ in have:
        print('  10741 もうある: %s' % typ)
        continue
    e['tickets'].append({'type': typ, 'date': d, 'url': u, 'soldout': True, 'soldoutSince': TODAY})
    print('  10741 ＋ %s（予定枚数終了）' % typ)

for i, names in VENUE_ADD.items():
    ev = byid[i]
    v = ev.get('venue') or ''
    add = [n for n in names if n not in v]
    if not add:
        continue
    mm = re.match(r'^(全国ツアー（)(.*)(）)$', v)
    if mm:
        nv = mm.group(1) + mm.group(2) + '／' + '／'.join(add) + mm.group(3)
    else:
        nv = '／'.join([v] + add) if v else '／'.join(add)
    print('  id%s 会場: %s\n        → %s' % (i, v, nv))
    ev['venue'] = nv

if not APPLY:
    print('（--apply で書き込み）')
    sys.exit(0)
nl = '\r\n' if '\r\n' in src else '\n'
arr = json.dumps(events, ensure_ascii=False, indent=2).replace('\n', nl)
out = src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():]
open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
