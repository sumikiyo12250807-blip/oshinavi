# -*- coding: utf-8 -*-
"""id5014 RAY YUZUKA AUTUMN EVENT 2026 “Salon de RAY” を直す（削除ではなく修復）。

2026-09-10 朝、期限切れの削除候補に出たが**消してはいけない子**だった。
検証エージェントが止め、あたしがぴあの実ページで裏を取った：

  https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670376
    公演期間  2026/9/9(水)・2026/9/19(土)
    会場      銀座ブロッサム（中央会館）(東京都) ／ 東京建物 Brillia HALL 箕面 大ホール (大阪府)
    ［出演］  柚香光
    一般発売＜9/19(土)公演＞ … **予定枚数終了**

直すこと:
  ① date を千秋楽 9/19 に（大阪初日で止まっていた＝[[feedback_longrun_event]]）
  ② dateLabel / venue / prefecture を2会場の事実に
  ③ artist を「柚香光」に（公演名が入っていて**本人名で検索しても出てこなかった**＝id4119 と同じ型）
  ④ 東京9/19の一般発売を **soldout（予定枚数終了）で追加**
     ＝売り切れは消さずに出し続ける（[[feedback_soldout_keep_visible]]）
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

BUNDLE = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2670376'

src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))

hit = None
for e in events:
    if e['id'] == 5014:
        hit = e
assert hit, 'id5014 が無い'

hit['artist'] = '柚香光'
hit['date'] = '2026-09-19'
hit['dateLabel'] = '2026年9月9日(水)〜2026年9月19日(土) 東京・大阪'
hit['venue'] = '全国ツアー（銀座ブロッサム（中央会館）／東京建物　Ｂｒｉｌｌｉａ　ＨＡＬＬ　箕面　大ホール）'
hit['prefecture'] = '東京・大阪'

types = {t.get('type') for t in hit.get('tickets') or []}
newt = {
    'type': '一般発売（東京 9/19公演）予定枚数終了',
    'date': '2026-09-19',
    'url': BUNDLE,
    'soldout': True,
    'soldoutSince': '2026-09-10',
}
if newt['type'] not in types:
    hit.setdefault('tickets', []).append(newt)

hit['verified'] = True
hit['verifiedAt'] = '2026-09-10'

print('id=5014 を直したわ')
print('  artist=%s / date=%s / prefecture=%s' % (hit['artist'], hit['date'], hit['prefecture']))
for t in hit['tickets']:
    print('   %-52s date=%s%s' % (t['type'][:52], t['date'], ' [予定枚数終了]' if t.get('soldout') else ''))

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)

arr = json.dumps(events, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(src[:m.start()] + m.group(1) + arr + m.group(3) + src[m.end():])
print('書き込み完了')
