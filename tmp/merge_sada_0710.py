# -*- coding: utf-8 -*-
"""id=1 さだまさし: ぴあ側の未登録7公演を統合して1エントリ化。
harvestがartist名一致で丸ごと除外していた取りこぼし([[feedback_harvest_name_dedup_blindspot]])。
楽天の兵庫・京都枠(予定枚数終了まで)は購入導線が楽天なので t.url 無しで残す
（renderCard: itemLinkUrl = t.url || links.rakuten）。ぴあ枠は t.url で会場別に飛ばす。"""
import re, json, sys, io
sys.path.insert(0, 'tools')
from build_pia_entries import build

out = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
URLS = [
    'https://t.pia.jp/pia/event/event.do?eventBundleCd=b2667141',
    'https://t.pia.jp/pia/event/event.do?eventCd=2548143',
    'https://t.pia.jp/pia/event/event.do?eventCd=2603976',
    'https://t.pia.jp/pia/event/event.do?eventCd=2616472',
    'https://t.pia.jp/pia/event/event.do?eventCd=2616473',
    'https://t.pia.jp/pia/event/event.do?eventCd=2618254',
    'https://t.pia.jp/pia/event/event.do?eventCd=2620025',
]
ne = build({'newid': 1, 'artist': 'さだまさし', 'urls': URLS})
if ne is None:
    out.write('ぴあ側に買える枠ゼロ→統合しない\n'); out.flush(); sys.exit(0)

idx = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', idx, re.S)
EVENTS = json.loads(m.group(2))
ev = next(e for e in EVENTS if e['id'] == 1)

rakuten_tickets = [t for t in ev['tickets'] if not t.get('url')]
merged = rakuten_tickets + ne['tickets']
# 販売終了日の近い順（[[feedback_display_order]] はカード内も販売中優先だが並びはrenderCard側で処理）
merged.sort(key=lambda t: t.get('date') or '9999-99-99')

ev['name'] = 'さだまさしコンサートツアー2026 神さまの言うとおり'
ev['tickets'] = merged
ev['venue'] = '全国ツアー（神戸国際会館こくさいホール／ロームシアター京都メインホール／' + \
              re.sub(r'^全国ツアー（|）$', '', ne['venue']) + '）' if ne['venue'].startswith('全国ツアー') else ne['venue']
ev['prefecture'] = '全国'
ev['date'] = max(ne['date'], '2026-08-19')
ev['dateLabel'] = ne.get('dateLabel') or ev['dateLabel']
ev['links']['pia'] = URLS[0]
ev['verifiedAt'] = '2026-07-10'
ev.pop('saleEndUnknown', None)

out.write(f"name: {ev['name']}\nvenue: {ev['venue']}\ndate: {ev['date']}\ndateLabel: {ev['dateLabel']}\n")
out.write(f"tickets {len(ev['tickets'])}枠:\n")
for t in ev['tickets']:
    out.write(f"   {t.get('startDate')} -> {t.get('date')} | {t.get('type')} | url={'有' if t.get('url') else '無(楽天)'}\n")
out.flush()

if '--apply' not in sys.argv:
    out.write('(DRY)\n'); out.flush(); sys.exit(0)
new_arr = json.dumps(EVENTS, ensure_ascii=False, indent=2)
open('index.html.bak_0710_merge_sada','w',encoding='utf-8').write(idx)
open('index.html','w',encoding='utf-8').write(idx[:m.start()]+m.group(1)+new_arr+m.group(3)+idx[m.end():])
out.write('written\n'); out.flush()
