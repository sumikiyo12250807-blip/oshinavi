# -*- coding: utf-8 -*-
"""id5394 Bunkamura『グレンギャリー・グレンロス』に、ぴあの告知文にだけ出ている先行を1枠足す（2026-09-12）。
build_pia_entries の📣警告（券種カードに無い＝自動では足さない）より:
  ■東京公演 ぴあ最速抽選先行 受付期間：9/11(金) 11:00 ～ 9/16(水) 23:59  申込: https://pia.jp/v/ggr26ps/
公演は東京 IMM THEATER 11/6〜11/30 の1本だけ＝対象公演が1つに決まるので手で足す（url は申込ページ）。
使い方: python tmp/fix_5394_0912.py [--apply]
"""
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = open('index.html', encoding='utf-8').read()
m = re.search(r'(  const EVENTS = )(\[.*?\])(;)', src, re.S)
events = json.loads(m.group(2))
e = next(x for x in events if x['id'] == 5394)
assert e.get('prefecture') == '東京' and 'IMM THEATER' in (e.get('venue') or ''), '5394 の会場が想定と違う'
t = {'type': 'ぴあ最速抽選先行（東京 11/6〜11/30公演）〜9/16 23:59', 'date': '2026-09-16',
     'url': 'https://pia.jp/v/ggr26ps/'}
if any(x.get('type') == t['type'] for x in e['tickets']):
    print('もう足してある')
    sys.exit(0)
e['tickets'].append(t)
print('id5394 ＋%s  url=%s' % (t['type'], t['url']))
if '--apply' not in sys.argv:
    print('(--apply で書き込み)')
    sys.exit(0)
open('index.html', 'w', encoding='utf-8').write(
    src[:m.start()] + m.group(1) + json.dumps(events, ensure_ascii=False, indent=2) + m.group(3) + src[m.end():])
print('書き込み完了')
