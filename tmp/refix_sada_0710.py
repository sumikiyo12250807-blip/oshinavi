# -*- coding: utf-8 -*-
"""id=1 さだまさし 作り直し。

【反省】ぴあ artistsページのHTMLから拾った ticketInformation.do?eventCd= 6件を
中身を確認せず「さだまさしの公演」と決めつけて統合した→実際は別公演だった
（2548143=新国立劇場オペラ『イタリアのトルコ人』/ 2603976=劇団☆新感線『アケチコ！』/
  2616472=ミュージカル『SPY×FAMILY 2』…= artistsページ内の別枠）。
ユーザー指摘で発覚。[[feedback_no_speculation]] [[feedback_bundle_full_rederive]]

正しいソースは bundle b2667141 のみ（ユーザー提供）。ここからゼロ再導出する。
併せて楽天の兵庫(8/17)・京都(8/19)枠もぴあ実ページで「予定枚数終了」と確認 → 除去。
楽天で買える枠がゼロになったため links.rakuten も外し、購入導線はぴあへ。
"""
import re, json, sys, io
sys.path.insert(0, 'tools')
from build_pia_entries import build

out = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
BUNDLE = 'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2667141'

ne = build({'newid': 1, 'artist': 'さだまさし', 'urls': [BUNDLE]})
if ne is None:
    out.write('ぴあ買える枠ゼロ→エントリ削除候補\n'); out.flush(); sys.exit(0)

idx = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S)
EVENTS = json.loads(m.group(2))
ev = next(e for e in EVENTS if e['id'] == 1)

ev['name'] = 'さだまさしコンサートツアー2026 神さまの言うとおり'
ev['tickets'] = ne['tickets']
ev['venue'] = ne['venue']
ev['prefecture'] = ne['prefecture']
ev['date'] = ne['date']
ev['dateLabel'] = ne['dateLabel']
ev['links']['pia'] = BUNDLE
ev['links']['rakuten'] = None   # 楽天扱いの兵庫・京都は予定枚数終了
ev['verifiedAt'] = '2026-07-10'
ev.pop('saleEndUnknown', None)

out.write(f"name: {ev['name']}\nvenue: {ev['venue']}\nprefecture: {ev['prefecture']}\n")
out.write(f"date: {ev['date']}\ndateLabel: {ev['dateLabel']}\n")
out.write(f"tickets {len(ev['tickets'])}枠:\n")
for t in ev['tickets']:
    out.write(f"   {t.get('startDate')} -> {t.get('date')} | {t.get('type')}\n")
out.flush()

if '--apply' not in sys.argv:
    out.write('(DRY)\n'); out.flush(); sys.exit(0)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html.bak_0710_refix_sada','w',encoding='utf-8').write(idx)
open('index.html','w',encoding='utf-8').write(idx[:m.start()]+m.group(1)+new_arr+m.group(3)+idx[m.end():])
out.write('written\n'); out.flush()
