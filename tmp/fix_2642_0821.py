# -*- coding: utf-8 -*-
"""2642 第108回全国高等学校野球選手権大会を救済する。

check_expired が「公演終了(8/20)・全販売終了」で削除候補に挙げたが、
reconcile_pia --ids で **ぴあに買える7枠（＜決勝＞一般発売・8/21 10:00発売）** が見つかった。
＝準決勝までしか登録しておらず、決勝(8/22)が丸ごと抜けていた。削除したら誤削除だった。

出典＝ https://t.pia.jp/pia/event/event.do?eventBundleCd=b2669702
（tools/build_pia_entries.py で機械構築 → tmp/built_2642.json）
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

built = json.load(io.open('tmp/built_2642.json', encoding='utf-8'))[0]
tickets = built['tickets']
assert len(tickets) == 7, len(tickets)
assert built['date'] == '2026-08-22', built['date']

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
n = 0
for e in EVENTS:
    if e['id'] != 2642:
        continue
    print('before: 枠%d / date=%s / dateLabel=%s' % (len(e.get('tickets') or []), e.get('date'), e.get('dateLabel')))
    e['tickets'] = tickets
    e['date'] = '2026-08-22'
    e['dateLabel'] = '2026年8月22日(土) 兵庫'
    e['verifiedAt'] = '2026-08-21'
    n += 1
    print('after : 枠%d / date=%s' % (len(tickets), e['date']))
    for t in tickets:
        print('   -', t['type'])

assert n == 1
shutil.copyfile('index.html', 'index.html.bak_0821_koshien')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('=== 更新 ===')
