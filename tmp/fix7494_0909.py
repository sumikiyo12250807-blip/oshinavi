# -*- coding: utf-8 -*-
"""id7494 木下グループジャパンオープンテニス＝作られた締切を外し、実ページどおりにする。

実ページ https://ticket.rakuten.co.jp/sports/rtep928/ を自分で開いて読んだ（2026-09-09）:
  販売期間: 一般発売  2026/08/01(土) 12:00 〜   ← **終わりが書かれていない**
いまの登録は「〜9/30 23:59」＝**ページのどこにも書かれていない日付**。
しかも大会は 9/28〜10/6 なので、途中で切れているのも辻褄が合わない。

id7502 と同じ形に倒す（ユーザー決定 2026-09-09）＝発売日に〜を付けて販売中で出す。
"""
import io, re, json, sys
sys.stdout.reconfigure(encoding='utf-8')

h = io.open('index.html', encoding='utf-8', newline='').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 7494)
assert len(e['tickets']) == 1, '枠が1つでない。中止'
t = e['tickets'][0]
old = t['type']
assert '〜9/30 23:59' in old, '中身が違う。中止'

t['type'] = old.replace('〜9/30 23:59', '8/1 12:00発売〜')
t['startDate'] = '2026-08-01'
t['date'] = '2026-10-06'          # 千秋楽＝画面から消えないための下限（表示には出さない）
t['saleEndUnknown'] = True

print('旧: %s' % old)
print('新: %s' % t['type'])
print('startDate=%s date=%s saleEndUnknown=%s' % (t['startDate'], t['date'], t['saleEndUnknown']))

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
out = h[:m.start(2)] + json.dumps(events, ensure_ascii=False, indent=2).replace('\n', '\r\n') + h[m.end(2):]
io.open('index.html', 'w', encoding='utf-8', newline='').write(out)
print('書き込み完了')
