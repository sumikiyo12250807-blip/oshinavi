# -*- coding: utf-8 -*-
"""id7502 ラフ×ラフ47都道府県巡業＝作られた締切を外し、実ページどおりの形にする。

実ページ https://ticket.rakuten.co.jp/music/rtal267/ を自分で開いて読んだ（2026-09-09）:
  販売期間: 一般発売  2026/08/17(月) 12:00 〜   ← **終わりが書かれていない**
  公演は17会場×昼13:00/夜16:30＝34本。すべて「購入する」が立っている。
いまの登録は「〜R9年 4/3 17:00」＝最終公演日(大阪4/3)を締切に流用した**嘘**。

直し方（ユーザー決定 2026-09-09）＝発売日に〜を付けて販売中で出す。
  type      … 「一般発売（…）8/17 12:00発売〜」
  startDate … 2026-08-17（発売日）
  date      … 2027-04-03（千秋楽＝画面から消えないための下限。表示には出さない）
  saleEndUnknown: true  ← これで renderCard が「8/17発売〜／販売中」と出す
"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 7502)
assert len(e['tickets']) == 1, '枠が1つでない。中止'
t = e['tickets'][0]
old_type = t['type']
assert '4/3 17:00' in old_type, '中身が違う。中止'

t['type'] = re.sub(r'〜R9年 4/3 17:00$', '8/17 12:00発売〜', old_type)
t['startDate'] = '2026-08-17'
t['date'] = '2027-04-03'
t['saleEndUnknown'] = True

print('旧: %s' % old_type)
print('新: %s' % t['type'])
print('startDate=%s date=%s saleEndUnknown=%s' % (t['startDate'], t['date'], t['saleEndUnknown']))

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
out = h[:m.start(2)] + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + h[m.end(2):]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
