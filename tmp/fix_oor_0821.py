# -*- coding: utf-8 -*-
"""4334 ONE OK ROCK の取りこぼしを回収する（ユーザー指摘 2026-08-21「ぴあにいっぱいある　取りこぼし」）。

きっかけ＝ユーザーが GIP（https://www.gip-web.co.jp/t/ONEOKROCK）で
「入場券は SOLD OUT だがシャトルバスが出ている」のを見つけ、ぴあにも同じものがあると教えてくれた。
ぴあをアーティスト名で掃き直したら、**本人名義で3つのeventCdが未登録**だった
（[[feedback_pia_bundle_hides_shows]]＝まとめページに出てこない枠はアーティスト名で引くと出る）。

  2631556 ＜クロークチケット＞          宮城 8/25（〜8/24 23:59）／8/26（〜8/25 23:59）受付中
  2628235 〈JR仙台駅東口発臨時直行往復バス券〉 宮城 8/25〜8/26（〜8/25 23:59）受付中
  2628239 〈駐車券〉                    宮城 8/25〜8/26（〜8/25 23:59）受付中

バス券だけ build 時にぴあの混雑ページへ飛ばされたので、tools/pia_tickets.py で単独確認して手で足す。
🚨券種名の頭に「公演 」が残る崩れがあったので直す。
"""
import io, re, json, sys, shutil
sys.stdout.reconfigure(encoding='utf-8')

built = json.load(io.open('tmp/oor_built.json', encoding='utf-8'))[0]
tickets = []
for t in built['tickets']:
    t = dict(t)
    t['type'] = re.sub(r'^公演\s*', '', t['type'])
    tickets.append(t)
# 混雑ページで落ちたバス券を手で足す（pia_tickets.py で実ページを確認済み）
tickets.append({
    'type': '一般発売【JR仙台駅東口発 臨時直行往復バス券】（宮城 8/25〜8/26公演）〜8/25 23:59',
    'date': '2026-08-25',
    'url': 'https://t.pia.jp/pia/event/event.do?eventCd=2628235',
})

h = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EVENTS = json.loads(m.group(2))
n = 0
for e in EVENTS:
    if e['id'] != 4334:
        continue
    print('before 枠%d / venue=%s / date=%s' % (len(e['tickets']), e.get('venue'), e.get('date')))
    e['tickets'] = tickets
    e['venue'] = built['venue']
    e['prefecture'] = built['prefecture']
    e['date'] = built['date']
    e['dateLabel'] = built.get('dateLabel')
    e['verifiedAt'] = '2026-08-21'
    print('after  枠%d / venue=%s / date=%s' % (len(tickets), e['venue'], e['date']))
    for t in tickets:
        print('   -', t['type'])
    n += 1
assert n == 1
shutil.copyfile('index.html', 'index.html.bak_0821_oor')
open('index.html', 'w', encoding='utf-8').write(
    h[:m.start()] + m.group(1) + json.dumps(EVENTS, ensure_ascii=False, indent=2) + m.group(3) + h[m.end():])
print('=== 更新 ===')
