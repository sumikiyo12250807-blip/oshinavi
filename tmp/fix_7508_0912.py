# -*- coding: utf-8 -*-
"""id7508 あつこ&タニケン を、ぴあの生ページ（b2671021・2026-09-12 朝に読んだ tmp/tanikene_b2671021.txt）に合わせる。

  ・宮城 11/14 の枠名＝登録は「プリセール」、ぴあは今「先行受付（先着順）」＝同じ窓の呼び名が変わっただけ
    → 名前だけ揃える（日付・URLはそのまま）。足すと同じ窓が2つ並ぶ
  ・大阪 2027/1/17 クレオ大阪東 の先行受付（先着順）9/12 12:00発売 が登録に無い → 足す
  ・会期を事実の 2026/11/14〜2027/1/17 に、会場と県に大阪を足す
使い方: python tmp/fix_7508_0912.py [--apply]
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
URL = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2671021'

# 🚨改行の作法＝読みも書きも既定のまま（newline を指定しない）＝CRLFが往復で保たれる
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 7508)
before = json.dumps(e, ensure_ascii=False, indent=1)

n_ren = 0
for t in e['tickets']:
    if t.get('type') == 'プリセール（宮城 11/14公演）9/12 12:00発売':
        t['type'] = '先行受付（先着順）（宮城 11/14公演）9/12 12:00発売'
        n_ren += 1
assert n_ren == 1, '宮城の枠が見つからない／複数ある: %d' % n_ren

osaka = '先行受付（先着順）（大阪 R9年 1/17公演）9/12 12:00発売'
assert not any(t.get('type') == osaka for t in e['tickets']), '大阪の枠はもうある'
e['tickets'].append({'type': osaka, 'date': '2026-09-12', 'startDate': '2026-09-12', 'url': URL})

e['date'] = '2027-01-17'
e['dateLabel'] = '2026年11月14日(土)〜2027年1月17日(日) 宮城・東京・愛知・大阪'
e['venue'] = '全国ツアー（トークネットホール仙台 小ホール／世田谷区・烏山区民会館 ホール／豊橋市民文化会館／クレオ大阪東）'
e['prefecture'] = '宮城・東京・愛知・大阪'

print('--- 前 ---\n' + before)
print('--- 後 ---\n' + json.dumps(e, ensure_ascii=False, indent=1))
if '--apply' not in sys.argv:
    print('\n(--apply で書き込み)')
    sys.exit(0)
open('index.html', 'w', encoding='utf-8').write(
    src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
print('書き込み完了')
