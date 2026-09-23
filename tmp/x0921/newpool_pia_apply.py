# -*- coding: utf-8 -*-
"""9/21夜の新着の名前でぴあを総ざらいして見つかった抜けを id8189 OWV（ぴあのツアーエントリ）に入れる。
  ① Zepp Namba 9/27 の「一般発売」＝登録は〜9/17のまま、ぴあは〜9/27 20:00 に延びていた（reconcile_pia の MISSING）
     → 同じ券種の締切が動いたので差し替える（b2668777 を組み直した tmp/x0921/newpool_pia_built2.json）
  ② 両国国技館 12/13（OWV LIVE TOUR 2026 -SQUAD- の東京公演）のぴあ「プレリザーブ〜9/28」が登録に無かった
     → ツアーは1エントリ＝id8189 に会場別URL付きで足し、日付・会場・県を2会場に広げる（tmp/x0921/newpool_pia_built.json の 960002）
  NMB48 b2671126（オリックス劇場）＝プリセール〜9/22 で id4952 と同じ枠＝足さない。
  せやねん！寄席 2631235＝ぴあは売切で組み上がらない＝FANYの id19499 で登録済み。
読み書きは inject_built.py と同じ（newline='' で CRLF を保つ）。
使い方: python tmp/x0921/newpool_pia_apply.py [--apply]
"""
import io
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
P = 'index.html'
b1 = {e['id']: e for e in json.load(io.open('tmp/x0921/newpool_pia_built.json', encoding='utf-8'))}
b2 = {e['id']: e for e in json.load(io.open('tmp/x0921/newpool_pia_built2.json', encoding='utf-8'))}
h = io.open(P, encoding='utf-8', newline='').read()
NL = '\r\n' if '\r\n' in h else '\n'
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', h, re.S)
EV = json.loads(m.group(2))
by = {e['id']: e for e in EV}

d = by[8189]
assert d['artist'] == 'OWV' and d['venue'] == 'Zepp Namba（OSAKA）', d
old = [t for t in d['tickets'] if t['type'].startswith('一般発売（大阪 9/27公演）')]
assert len(old) == 1 and len(d['tickets']) == 1, d['tickets']
zn = b2[960004]['tickets']
assert len(zn) == 1 and zn[0]['type'] == '一般発売（大阪 9/27公演）〜9/27 20:00', zn
ry = b1[960002]['tickets']
assert len(ry) == 1 and ry[0]['type'] == 'プレリザーブ（東京 12/13公演）〜9/28 23:59', ry

t1 = dict(zn[0]); t1['url'] = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2668777'
t2 = dict(ry[0]); t2['url'] = 'https://t.pia.jp/pia/event/event.do?eventCd=2633776'
print('差し替え id8189 %s → %s' % (old[0]['type'], t1['type']))
print('足し込み id8189 + %s %s' % (t2['type'], t2['url']))
d['tickets'] = [t1, t2]
d['date'] = '2026-12-13'
d['dateLabel'] = '2026年9月27日(日)〜2026年12月13日(日) 大阪・東京'
d['venue'] = '全国ツアー（Zepp Namba（OSAKA）／両国国技館）'
d['prefecture'] = '大阪・東京'
d['verifiedAt'] = '2026-09-21'

if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
arr = json.dumps(EV, ensure_ascii=False, indent=2).replace('\n', NL)
io.open(P, 'w', encoding='utf-8', newline='').write(h[:m.start()] + m.group(1) + arr + m.group(3) + h[m.end():])
print('書き込み完了 id8189')
